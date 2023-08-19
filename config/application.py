import tornado.web
import json

from app import settings
from .database import Sql
from app.utils.constants import Key, Environment, Token
from app.utils.authentication_authorization import TokenDetail


# for url mappings
import re
from app.handlers.login_handler import LoginHandler
from app.handlers.forgot_password_handler import ForgotPasswordHandler


class Application():

    def initialize(self, environment):
        app = tornado.web.Application(
            UrlMapping().get_all(),
            debug=(True if environment == Environment.DEVELOPMENT else False)
        )

        config = self.read_configuration()
        app.mysql_connections = Sql().initialize(config)
        app.token_detail = self.get_token_detail(config)

        if Key.SECRET_COOKIE_KEY in config:
            app.settings[Key.SECRET_COOKIE_KEY] = config[Key.SECRET_COOKIE_KEY]
            print(f'\nCoookie secret key has been set successfully')
        else:
            raise ValueError(f"Missing configuration for '{Key.SECRET_COOKIE_KEY}'")

        app.settings[settings.TEMPLATE_PATH_KEY] = settings.TEMPLATE_PATH
        print(f"\nTemplate path: {settings.TEMPLATE_PATH}")
        print(f"Static path: {settings.STATIC_PATH}")

        return app
    
    
    def read_configuration(self):
        config_file = settings.CONFIG_PATH+'\\'+settings.CONFIG_FILE_NAME
        print(f'\nReading configuration from {config_file} ...')

        with open(config_file, 'r') as file:
            data = json.load(file)

        return data
    
        
    def get_token_detail(self, config):        
        if Key.TOKEN in config:
            print('\n---------- Getting token details ----------')
            token = config[Key.TOKEN]
            token_detail = TokenDetail

            if Token.PRIVATE_KEY in token:
                token_detail.private_key = token[Token.PRIVATE_KEY]
            else:
                raise ImportError(f"Missing configuration for '{Token.PRIVATE_KEY}'")
            
            if Token.EXPIRE_DURATION in token:
                token_detail.expire_duration = token[Token.EXPIRE_DURATION]
            else:
                print(f"Missing configuration for '{Token.EXPIRE_DURATION}' -> Putting {Token.DEFAULT_EXPIRE_DURATION} hours as default")
                token_detail.expire_duration = Token.DEFAULT_EXPIRE_DURATION
            
            if Token.ALGORITHM in token:
                token_detail.algorithm = token[Token.ALGORITHM]
            else:
                print(f"Missing configuration for token '{Token.ALGORITHM}' -> Putting {Token.DEFAULT_ALGORITHM} as default")
                token_detail.algorithm = Token.DEFAULT_ALGORITHM
        
            return token_detail
        else:
            raise ConnectionError(f'Missing configuration for token')
    
    
class UrlMapping():
    def get_all(self):
        print('\n---------- Initializing url -> handlers ----------')

        handlers = [
            (fr"/login", LoginHandler),
            (fr"{settings.STATIC_URL}", tornado.web.StaticFileHandler, {"path": settings.STATIC_PATH}),
            (fr"/forgot-password", ForgotPasswordHandler),
        ]

        for i, handler in enumerate(handlers):
            print(f'{i+1}. {handler[0]} -> {self.get_handler_name(handler[1])}')

        return handlers

    def get_handler_name(self, _class):
        class_name = re.search(r"'(.*?)'", str(_class)).group(1)
        return str(class_name)

