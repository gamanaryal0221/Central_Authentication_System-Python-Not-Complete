from typing import Awaitable, Optional
import tornado.web
import tornado.ioloop

from app.utils.constants import Template, Key, Mysql
from app.utils.common import render_error_page
from app.utils.db_utils import get_connection, get_client_and_service_details_from_hosturl, get_user_detail
from app.utils.authentication_authorization import Access

class ForgotPasswordHandler(tornado.web.RequestHandler):
    def prepare(self) -> Awaitable[None] | None:

        host_url = self.get_argument(Key.HOST_URL, None)
        print(f"host_url:{host_url}")

        if host_url is not None:
            connection = get_connection(self, Mysql.RESOURCE_MANAGER)
            client_service = get_client_and_service_details_from_hosturl(connection, host_url)

            if client_service is not None and client_service.get(Key.CLIENT_ID) and client_service.get(Key.SERVICE_ID):
                self.request.client_service =client_service
                self.request.response = {
                    Key.ERROR_MSG: None,
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
        username = self.get_argument(Key.USERNAME, None)

        response = self.request.response
        response[Key.USERNAME] = username

        if username:
            print(f"\nVerifying the provided email or username:{username} ...")
            try:
                connection = get_connection(self, Mysql.RESOURCE_MANAGER)
                user = get_user_detail(connection, username)
                
                if user:
                    if Access.is_valid_for_respective_client_service(connection, user, self.request.client_service):
                        print(f"Access verified for user[id:{user[Key.USER_ID]}] on host_url:{response[Key.HOST_URL]}")

                        try:
                            # Sent the password reset mail to the user
                            response[Key.ERROR_MSG] = "Login successfull"
                            self.render(Template.FORGOT_PASSWORD,**response)
                        except Exception as e:
                            print(str(e))
                            print('Error occured in token generation -> Redirecting to login page')
                            response[Key.ERROR_MSG] = "Something went wrong. Please try again later"
                            self.render(Template.FORGOT_PASSWORD,**response)
                    else:
                        render_error_page(
                            self, status_code=403, title="Forbidden", redirect_url=f"/forgot-password?host_url={response[Key.HOST_URL]}", redirect_text="Try Again",
                            message=f"Sorry, We can not allow you to reset your password in this url for now."
                        )
                else:
                    response[Key.ERROR_MSG] = "Please provide your correct email or username and try again."
                    self.render(Template.FORGOT_PASSWORD,**response)
            except Exception as e:
                print(str(e))
                render_error_page(self, redirect_url=f"/forgot-password?host_url={response[Key.HOST_URL]}", redirect_text="Try Again")
        else:
            response[Key.ERROR_MSG] = "Email or Username is mandatory"
            self.render(Template.FORGOT_PASSWORD, **response)


