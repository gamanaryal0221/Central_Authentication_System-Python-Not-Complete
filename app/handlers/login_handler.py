from typing import Awaitable
import tornado.web
import tornado.ioloop

import traceback

from app.interceptors import Interceptors

import json

from app.utils.constants import Template, Key, Mysql
from app.utils.common import get_splitted_url
from app.utils.db_utils import get_connection, get_user_detail_by_email_username_or_number
from app.utils.authentication_authorization import Password, Access
from app.utils.token import JwtToken

class LoginHandler(tornado.web.RequestHandler):

    @Interceptors.request_interceptor
    def get(self):
        self.render(Template.LOGIN, **self.request.response)

    @Interceptors.request_interceptor
    def post(self):
        print(f"\nVerifying the credentials ...")
        connection = None
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            print(data)

            username = data.get(Key.USERNAME)
            password = data.get(Key.PASSWORD)

            if not (username and password):
                self.finish({Key.MESSAGE:"All fields are mandatory"})
                return

            connection = get_connection(self, Mysql.USER_MANAGEMENT)
            user = get_user_detail_by_email_username_or_number(connection, username, True)
            print(f"User[id:{user[Key.USER_ID]}, username:{user[Key.USERNAME]}]")
            
            if not user:
                self.finish({Key.MESSAGE:"Login failed. Please check your credentials and try again."})
                return

            if not Password(password).is_correct(user):
                self.finish({Key.MESSAGE:"Provided credentials is not determined to be authentic."})
                return

            print(f"Credentials verified for user[id:{user[Key.USER_ID]}]")
            client_service = self.request.client_service

            if not Access.is_valid_for_respective_client_service(connection, user, self.request.client_service):
                self.finish({Key.MESSAGE:"You do not have access on this application"})
                return

            host_url = client_service[Key.HOST_URL]
            print(f"Access verified for user[id:{user[Key.USER_ID]}] on host_url:{host_url}")

            login_success_token = JwtToken(self, JwtToken.Purpose.LOGIN_SUCCESSFUL).generate(user, client_service, host_url)
            if not login_success_token:
                raise RuntimeError(f"Received login success token:{login_success_token}")
            

            full_request_host = get_splitted_url(host_url)[Key.FULL_REQUEST_HOST]
            if not full_request_host:
                raise RuntimeError(f"Received full_request_host:{full_request_host}")

            # redirection_url = ("https://" if "https://" in host_url else "http://") if host_url else "https://"
            # redirection_url = redirection_url + full_request_host + "/login/success"

            # Setting data in cookie
            authentication_cookie_key = str(full_request_host+"_user_authentication_data").replace(".","_").replace(":","_")
            user_authentication_data = {Key.TOKEN: login_success_token, Key.HOST_URL:host_url}
            # self.set_secure_cookie(authentication_cookie_key, tornado.escape.json_encode(user_authentication_data), domain=".um.dev.vcp.com:8800", path="/")
            self.set_secure_cookie(authentication_cookie_key, "demo", domain=".dev.vcp.com", path="/")

            print("#########################################")
            print(authentication_cookie_key)
            print(self.get_secure_cookie(authentication_cookie_key))

            host_url = host_url + "/login/success"
            print(f"Redirection URL:{host_url}\n - full_request_host:{full_request_host}\n - host_url:{host_url}")
            self.redirect(host_url)

        except Exception as e:
            traceback.print_exception(e)
            self.finish({Key.MESSAGE:"Something went wrong Please try again"})
            return
        
        finally:
            if connection:
                connection.close()

        