import tornado.web

from .configurations import Configurations

from app.utils.constants import Key, Environment
from app.utils.common import fetch_data

from app import settings

# for url mappings
import re
from app.handlers.login_handler import LoginHandler
from app.handlers.forgot_password_handler import ForgotPasswordHandler
from app.handlers.reset_password_handler import ResetPasswordHandler


class Application():

    def initialize(self, environment):
        app = tornado.web.Application(
            UrlMapping().get_all(),
            debug=(True if environment == Environment.DEVELOPMENT else False)
        )

        configuration = Configurations()
        app.config = configuration.initialize(environment)

        config_file = configuration.config_file
        app.settings[Key.SECRET_COOKIE_KEY] = fetch_data(config_file, Key.SECRET_COOKIE_KEY)
        print(f'\nCoookie secret key has been set successfully')

        app.settings[settings.TEMPLATE_PATH_KEY] = settings.TEMPLATE_PATH
        print(f"\nTemplate path: {settings.TEMPLATE_PATH}")
        print(f"Static path: {settings.STATIC_PATH}")

        port = fetch_data(config_file, Key.PORT, -1)
        if port != -1:
            print(f"\nListening to port:{port}")
            app.listen(port)

        return app

    
class UrlMapping():
    def get_all(self):
        print('\n---------- Initializing url -> handlers ----------')

        handlers = [
            (fr"/login", LoginHandler),
            (fr"{settings.STATIC_URL}", tornado.web.StaticFileHandler, {"path": settings.STATIC_PATH}),
            (fr"/forgot-password", ForgotPasswordHandler),
            (fr"/reset-password", ResetPasswordHandler),
        ]

        for i, handler in enumerate(handlers):
            print(f'{i+1}. {handler[0]} -> {self.get_handler_name(handler[1])}')

        return handlers

    def get_handler_name(self, _class):
        class_name = re.search(r"'(.*?)'", str(_class)).group(1)
        return str(class_name)

