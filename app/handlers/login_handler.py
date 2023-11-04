from typing import Awaitable
import tornado.web
import tornado.ioloop

from app.utils.constants import Template, Key, Mysql, Default
from app.utils.common import render_error_page, login_succes_redirect_to_application
from app.utils.db_utils import get_connection, get_client_and_service_details_from_hosturl_or_request_host, get_user_detail_by_email_username_or_number
from app.utils.authentication_authorization import Password, Access
from app.utils.token import JwtToken

class LoginHandler(tornado.web.RequestHandler):
    def prepare(self) -> Awaitable[None] | None:

        host_url = self.get_argument(Key.HOST_URL, None)
        print(f"host_url:{host_url}")

        if host_url is not None:
            connection = get_connection(self, Mysql.RESOURCE_MANAGER)
            client_service = get_client_and_service_details_from_hosturl_or_request_host(connection, host_url, None)

            if client_service is not None and client_service.get(Key.CLIENT_ID) and client_service.get(Key.SERVICE_ID):
                self.request.client_service =client_service
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
        self.render(Template.LOGIN, **self.request.response)

    
    def post(self):
        username = self.get_argument(Key.USERNAME, None)
        password = self.get_argument(Key.PASSWORD, None)

        response = self.request.response
        response[Key.USERNAME] = username

        if username and password:
            print(f"\nVerifying the credentials ...")

            host_url = response[Key.HOST_URL]
            redirect_to_log_url = f"/login?host_url={host_url}"

            try:
                connection = get_connection(self, Mysql.RESOURCE_MANAGER)
                user = get_user_detail_by_email_username_or_number(connection, username, True)
                
                if user:
                    if Password(password).is_correct(user):
                        print(f"Credentials verified for user[id:{user[Key.USER_ID]}]")
                        client_service = self.request.client_service

                        if Access.is_valid_for_respective_client_service(connection, user, self.request.client_service):
                            print(f"Access verified for user[id:{user[Key.USER_ID]}] on host_url:{host_url}")

                            try:
                                login_succes_redirect_to_application(
                                    self, client_service[Key.REQUEST_HOST], host_url,
                                    JwtToken(self, JwtToken.Purpose.LOGIN_SUCCESSFUL).generate(user, client_service, host_url)
                                )
                            except Exception as e:
                                print(str(e))
                                render_error_page(self, redirect_url=redirect_to_log_url, redirect_text="Try Again")
                        else:
                            render_error_page(
                                self, status_code=403, title="Forbidden", redirect_url=redirect_to_log_url, redirect_text="Try Again",
                                message=f"You do not have on '{client_service[Key.SERVICE_DISPLAY_NAME]}' service of {client_service[Key.CLIENT_DISPLAY_NAME]}"
                            )
                    else:
                        response[Key.STATUS_MSG] = f"Provided credentials is not determined to be authentic."
                        self.render(Template.LOGIN,**response)
                else:
                    response[Key.STATUS_MSG] = "Login failed. Please check your credentials and try again."
                    self.render(Template.LOGIN,**response)
            except Exception as e:
                print(str(e))
                render_error_page(self, redirect_url=redirect_to_log_url, redirect_text="Try Again")
        else:
            response[Key.STATUS_MSG] = "All fields are mandatory"
            self.render(Template.LOGIN, **response)