import tornado.web
import tornado.ioloop

import traceback

from app.utils.constants import Key, Mysql
from app.utils.common import render_error_page
from app.utils.db_utils import get_connection, get_client_service_detail


# from app.utils.db_utils import get_connection


class Interceptors(tornado.web.RequestHandler):

    @staticmethod
    def request_interceptor(func):
        def wrapper(self, *args, **kwargs):

            connection = None

            try:

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
                                Key.HOST_URL: host_url,
                                Key.CLIENT_DISPLAY_NAME: client_service[Key.CLIENT_DISPLAY_NAME],
                                Key.IS_GOOGLE_AUTHENTICATION_ENABLED: client_service[Key.IS_GOOGLE_AUTHENTICATION_ENABLED],
                                Key.IS_CREDENTIAL_AUTHENTICATION_ENABLED: client_service[Key.IS_CREDENTIAL_AUTHENTICATION_ENABLED],
                                Key.CLIENT_LOGO_URL: "https://www.freelogoservices.com/blog/wp-content/uploads/transparent-logo.jpg",
                                Key.BACKGROUND_IMAGE_URL: "https://file.ejatlas.org/img/Conflict/4211/thumb_sagarmatha-national-park-2.jpg"
                            }

                        return func(self, *args, **kwargs)
                        
                    else:
                        render_error_page(self, status_code=400, title="Bad Request", message="Malformed URL")
                else:
                    render_error_page(self, status_code=400, title="Bad Request", message="The request is missing a required parameter")

            except Exception as e:
                traceback.print_exception(e)
                render_error_page(self, self.request.full_url(), "Try Again")

            finally:
                if connection: connection.close()

        return wrapper
