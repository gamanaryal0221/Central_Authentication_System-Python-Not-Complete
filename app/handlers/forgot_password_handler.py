from typing import Awaitable
import tornado.web
import tornado.ioloop

import json

from app.utils.constants import Template, Key, Mysql, Default, Environment, Url
from app.utils.common import render_error_page
from app.utils.db_utils import get_connection, get_client_service_detail, get_user_detail_by_email_username_or_number
from app.utils.authentication_authorization import Access
from app.utils.token import JwtToken
from app.utils.email_sender import Email

class ForgotPasswordHandler(tornado.web.RequestHandler):
    def prepare(self) -> Awaitable[None] | None:

        host_url = self.get_argument(Key.HOST_URL, None)
        print(f"host_url:{host_url}")

        if host_url is not None:
            connection = get_connection(self, Mysql.USER_MANAGEMENT)
            client_service = get_client_service_detail(connection, host_url, None)

            if client_service is not None and client_service.get(Key.CLIENT_ID) and client_service.get(Key.SERVICE_ID):
                client_service[Key.HOST_URL] = host_url
                self.request.client_service =client_service

                if self.request.method == "GET":
                    self.request.response = {
                        Key.STATUS_MSG: None,
                        Key.STATUS_MSG_COLOR: Default.STATUS_MSG_COLOR,
                        Key.USERNAME: "",
                        Key.HOST_URL: host_url,
                        Key.CLIENT_DISPLAY_NAME: client_service[Key.CLIENT_DISPLAY_NAME],
                        Key.IS_GOOGLE_AUTHENTICATION_ENABLED: client_service[Key.IS_GOOGLE_AUTHENTICATION_ENABLED],
                        Key.IS_CREDENTIAL_AUTHENTICATION_ENABLED: client_service[Key.IS_CREDENTIAL_AUTHENTICATION_ENABLED],
                        Key.CLIENT_LOGO_URL: "https://www.freelogoservices.com/blog/wp-content/uploads/transparent-logo.jpg",
                        Key.BACKGROUND_IMAGE_URL: "https://file.ejatlas.org/img/Conflict/4211/thumb_sagarmatha-national-park-2.jpg"
                    }
            else:
                render_error_page(self, status_code=400, title="Bad Request", message="Malformed URL")
        else:
            render_error_page(self, status_code=400, title="Bad Request", message="The request is missing a required parameter")

        return super().prepare()
    

    def get(self):
        self.render(Template.FORGOT_PASSWORD, **self.request.response)


    def post(self):
        print(f"Forgot password - POST")
        username = self.get_argument(Key.USERNAME, None)

        response = self.request.response
        response[Key.USERNAME] = username

        if username:
            print(f"\nVerifying the provided email, username, or phone:{username} ...")

            host_url = response[Key.HOST_URL]
            redirect_url = f"/forgot-password?host_url={host_url}"

            try:
                connection = get_connection(self, Mysql.USER_MANAGEMENT)
                user = get_user_detail_by_email_username_or_number(connection, username)
                
                if user:
                    if Access.is_valid_for_respective_client_service(connection, user, self.request.client_service):
                        print(f"Access verified for user[id:{user[Key.USER_ID]}] on host_url:{host_url}")

                        try:
                            # Sent the password reset mail to the user
                            if is_reset_password_email_sent(self, connection, user, host_url):
                                response[Key.STATUS_MSG] = f"Password reset email has been successfully sent to your respective email address of '{response[Key.USERNAME]}'"
                                response[Key.STATUS_MSG_COLOR] = "green"
                                response[Key.USERNAME] = ""
                                self.render(Template.FORGOT_PASSWORD,**response)
                            else:
                                response[Key.STATUS_MSG] = "Something went wrong. Please try again later"
                                self.render(Template.FORGOT_PASSWORD,**response)
                        except Exception as e:
                            print(str(e))
                            response[Key.STATUS_MSG] = "Something went wrong. Please try again later"
                            self.render(Template.FORGOT_PASSWORD,**response)
                    else:
                        render_error_page(
                            self, status_code=403, title="Forbidden", redirect_url=redirect_url, redirect_text="Try Again",
                            message=f"Sorry, We can not allow you to reset your password in this url for now."
                        )
                else:
                    response[Key.STATUS_MSG] = "Please provide your correct email, username, or phone to proceed."
                    self.render(Template.FORGOT_PASSWORD,**response)
            except Exception as e:
                print(str(e))
                render_error_page(self, redirect_url=redirect_url, redirect_text="Try Again")
        else:
            response[Key.STATUS_MSG] = "Email or Username is mandatory"
            self.render(Template.FORGOT_PASSWORD, **response)


        print(f"\nForgot password - POST")
        connection = None
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            print(data)

            username = data.get(Key.USERNAME)

            if not username:
                self.finish({Key.MESSAGE:"Email, Username, or Phone is mandatory"})
                return

            connection = get_connection(self, Mysql.USER_MANAGEMENT)
            user = get_user_detail_by_email_username_or_number(connection, username, True)
            print(f"User[id:{user[Key.USER_ID]}, username:{user[Key.USERNAME]}]")
            
            if not user:
                self.finish({Key.MESSAGE:"Please provide your correct email, username, or phone to proceed."})
                return

            if not Access.is_valid_for_respective_client_service(connection, user, self.request.client_service):
                self.finish({Key.MESSAGE:"Sorry, We can not allow you to reset your password."})
                return

            client_service = self.request.client_service
            host_url = client_service[Key.HOST_URL]
            print(f"Access verified for user[id:{user[Key.USER_ID]}] on host_url:{host_url}")

            if is_reset_password_email_sent(self, connection, user, host_url):
                self.finish({Key.MESSAGE:Key.OK})
                return
            else:
                self.finish({Key.MESSAGE:"Something went wrong Please try again"})
                return

        except Exception as e:
            print(f"Error encountered while verifying credentials: {e} ")
            self.finish({Key.MESSAGE:"Something went wrong Please try again"})
            return
        
        finally:
            if connection:
                connection.close()


def is_reset_password_email_sent(_self, connection, user, host_url):
    email_address = user[Key.EMAIL]
    if email_address:
        try:
            password_reset_token = JwtToken(_self, JwtToken.Purpose.RESET_PASSWORD).generate(user, None, host_url, connection)
            cas_reset_password_url = get_cas_reset_password_url(_self, password_reset_token)
            content = get_reset_password_email_content(user[Key.USERNAME], cas_reset_password_url)
            return Email(_self).send(email_address, "Reset Password", content, None)
        except Exception as e:
            print(f"Error encounered while sending reset password email {e}")
            return False
    else:
        print("Email address not found to send the reset password mail")
        return False


def get_cas_reset_password_url(_self, password_reset_token):
    environment = _self.application.config[Environment.KEY]
    if environment == Environment.PRODUCTION: environment = ""

    cas_reset_password_url = Url.CAS_RESET_PASSWORD_URL.replace(Environment.KEY.upper(),environment).replace(Key.TOKEN.upper(),password_reset_token).rstrip("/")
    print(f"cas_reset_password_url:{cas_reset_password_url}")

    return cas_reset_password_url


def get_reset_password_email_content(user_fullname, password_reset_link):
    return f"password_reset_link:{password_reset_link}"
    # return f"""
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <style>
    #             body {{
    #                 font-family: Arial, Helvetica, sans-serif;
    #             }}
    #             .container {{
    #                 max-width: 600px;
    #                 margin: 0 auto;
    #                 padding: 20px;
    #                 text-align: center;
    #             }}
    #             .message {{
    #                 font-size: 16px;
    #                 line-height: 1.6;
    #                 margin-top: 20px;
    #             }}
    #             .cta-button {{
    #                 display: inline-block;
    #                 margin-top: 20px;
    #                 padding: 10px 20px;
    #                 background-color: #007BFF;
    #                 color: #fff;
    #                 text-decoration: none;
    #                 font-weight: bold;
    #                 border-radius: 5px;
    #             }}
    #         </style>
    #     </head>
    #     <body>
    #         <div class="container">
    #             <p class="message">
    #                 Hello {user_fullname},
    #             </p>
    #             <p class="message">
    #                 We received a request to reset your password. To proceed, click the button below:
    #             </p>
    #             <a class="cta-button" href="{password_reset_link}">Reset Password</a>
    #             <p class="message">
    #                 If you didn't request a password reset, please disregard this email.
    #             </p>
    #             <p class="message">
    #                 Thank you for using our service.
    #             </p>
    #         </div>
    #     </body>
    #     </html>
    #     """

