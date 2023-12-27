from typing import Awaitable
import tornado.web
import tornado.ioloop

from app.utils.token import JwtToken
from app.utils.db_utils import get_connection, get_user_detail_by_id, get_count_of_password_reset_using_token, update_password_of_a_user
from app.utils.common import render_error_page
from app.utils.constants import Template, Key, Mysql, Default
from app.utils.authentication_authorization import Password
from app.utils.email_sender import Email

class ResetPasswordHandler(tornado.web.RequestHandler):
    def prepare(self) -> Awaitable[None] | None:
        token = self.get_argument(Key.TOKEN, None)
        print(f"\nToken for password reset:{token}")

        if token:
            token_validation_response = JwtToken(self, JwtToken.Purpose.RESET_PASSWORD).validate(token)
            if token_validation_response:
                if token_validation_response[Key.IS_VALIDATED] is True:
                    print("Token is validated")

                    payload = token_validation_response[Key.PAYLOAD]

                    self.request.required = {
                        Key.TOKEN: token,
                        Key.USER_ID: payload[Key.USER_ID],
                        Key.CURRENT_COUNT_OF_PASSWORD_RESET_REQUEST_USING_TOKEN: payload[Key.CURRENT_COUNT_OF_PASSWORD_RESET_REQUEST_USING_TOKEN]
                    }

                    self.request.response = {
                        Key.TOKEN: token,
                        Key.STATUS_MSG: None,
                        Key.STATUS_MSG_COLOR: Default.STATUS_MSG_COLOR,
                        Key.CLIENT_DISPLAY_NAME: Default.COMPANY_NAME,
                        Key.IS_GOOGLE_AUTHENTICATION_ENABLED: False,
                        Key.IS_CREDENTIAL_AUTHENTICATION_ENABLED: True,
                        Key.CLIENT_LOGO_URL: "https://www.freelogoservices.com/blog/wp-content/uploads/transparent-logo.jpg",
                        Key.BACKGROUND_IMAGE_URL: "https://file.ejatlas.org/img/Conflict/4211/thumb_sagarmatha-national-park-2.jpg"
                    }

                else:
                    if token_validation_response[Key.IS_FORBIDDEN] is True:
                        render_error_page(self, status_code=403, title="Forbidden", message=token_validation_response[Key.MESSAGE])
                    else:
                        render_error_page(self, status_code=500, title="Server Error", message="Something went wrong. Please try again later")
            else:
                render_error_page(self, status_code=500, title="Server Error", message="Something went wrong. Please try again later")
        else:
            render_error_page(self, status_code=400, title="Bad Request", message="The request is missing a required parameter")

        return super().prepare()
    

    def get(self):
        self.render(Template.RESET_PASSWORD, **self.request.response)


    def post(self):
        password = self.get_argument(Key.PASSWORD, None)
        confirm_password = self.get_argument(Key.CONFIRM_PASSWORD, None)

        required = self.request.required
        response = self.request.response
        redirect_to_reset_password = f"/reset-password?token={required[Key.TOKEN]}"

        if password and confirm_password:
            if password == confirm_password:
                print(f"\nResetting password ...")

                user_id = required[Key.USER_ID]

                try:
                    connection = get_connection(self, Mysql.USER_MANAGEMENT)

                    previous_count_of_password_changed_using_token = get_count_of_password_reset_using_token(connection, user_id)
                    if previous_count_of_password_changed_using_token < required[Key.CURRENT_COUNT_OF_PASSWORD_RESET_REQUEST_USING_TOKEN]:

                        user = get_user_detail_by_id(connection, user_id, True)
                        
                        if user:

                            password = Password(password)
                            invalid_messages = password.check_validity()
                            if invalid_messages:
                                response[Key.STATUS_MSG] = invalid_messages
                                self.render(Template.RESET_PASSWORD, **response)
                            else:
                                hashed_password_detail = password.make()
                                if hashed_password_detail:
                                    if update_password_of_a_user(connection, user_id, hashed_password_detail):
                                        notify_password_reset_to_user_via_email(self, user)
                                        print("Password reset successfully")
                                        self.write("Password reset successfully")
                                    else:
                                        raise RuntimeError("Could not update password")
                                else:
                                    raise RuntimeError("Hashed password details is received null")
                        else:
                            raise RuntimeError("User is received null")
                    else:
                        render_error_page(self, status_code=403, title="Forbidden", message="The token has been already used to reset your password.\nIf it was not you, contact your administrator as soon as possible.")

                except Exception as e:
                    print(str(e))
                    render_error_page(self, redirect_url=redirect_to_reset_password, redirect_text="Try Again")

            else:
                response[Key.STATUS_MSG] = "Passwords are not matching"
                self.render(Template.RESET_PASSWORD, **response)
        else:
            response[Key.STATUS_MSG] = "All fields are mandatory"
            self.render(Template.RESET_PASSWORD, **response)



def notify_password_reset_to_user_via_email(_self, user):
    email_address = user[Key.EMAIL]
    if email_address:
        try:
            content = get_password_reset_notification_email_content(user[Key.USERNAME])
            return Email(_self).send(email_address, "Alert: Password Reset", content, None)
        except Exception as e:
            print(f"Error encounered while sending the success password reset mail: {e}")
    else:
        print("Email address not found to send the success password reset mail")


def get_password_reset_notification_email_content(user_fullname):
    return f"""
        <!DOCTYPE html>
        <html>
          <body>
              <p>Hello {user_fullname},</p>
              <p>Your password has been reset successfully.</p><br>
              <p>If it was not you, please contact your administrator as soon as possible.</p>
              <p>Thank You</p>
          </body>
        </html>
        """
