from typing import Awaitable, Optional
import tornado.web
import tornado.ioloop

from app.utils.constants import Template, Key, Mysql, Default
from app.utils.common import render_error_page, login_succes_redirect_to_application
from app.utils.db_utils import get_connection, get_client_and_service_details_from_hosturl, get_user_detail_by_email_username_or_number
from app.utils.authentication_authorization import Password, Access
from app.utils.token import JwtToken

class ResetPasswordHandler(tornado.web.RequestHandler):
    # def prepare(self) -> Awaitable[None] | None:
    #     return super().prepare()
    

    def get(self):
        self.write("Reset Password")