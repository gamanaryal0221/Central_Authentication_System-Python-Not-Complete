import datetime
import jwt

from enum import Enum
from .constants import Config, Key, Token

from .custom_exceptions import NotFoundInApplicationException

class JwtToken():
    
    class Purpose(Enum):
        LOGIN_SUCCESSFUL = "vcp.token.jwt.login.successful"
        RESET_PASSWORD = "vcp.token.jwt.forgot_password.reset"

    token_config = None
    purpose:Purpose = None

    def __init__(self, _self, _purpose:Purpose):
        print(f"Initializing token generation ...")
        if _purpose:
            if _purpose in self.Purpose:
                self.token_config = _self.application.config[Config.TOKEN]

                if self.token_config:
                    self.purpose = _purpose
                else:
                    raise NotFoundInApplicationException("Token config")
            else:
                raise RuntimeError(f"Invalid: Purpose for Jwt token generation")
        else:
            raise RuntimeError(f"Not Found: Purpose of Jwt token generation")


    def generate(self, user, client_service, host_url):
        _print = f"'{self.purpose.value}' for user[id:{user[Key.USER_ID]}]"
        print(f"Generating token {_print} ...")

        payload = {
            Key.TOKEN_PURPOSE: self.purpose.value,
            Key.USER_ID: user[Key.USER_ID],
            Key.EMAIL: user[Key.EMAIL],
            Key.USERNAME: user[Key.USERNAME],
            Key.NUMBER: user[Key.NUMBER],
            Key.FULLNAME: f"{user[Key.FIRST_NAME]}{' '+user[Key.MIDDLE_NAME] if user[Key.MIDDLE_NAME] else ''} {user[Key.LAST_NAME]}",
            Key.EXPIRE: datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_config[Token.EXPIRE_DURATION])
        }

        if client_service:
            payload[Key.CLIENT_ID] = client_service[Key.CLIENT_ID]
            payload[Key.CLIENT_NAME] = client_service[Key.CLIENT_NAME]
            payload[Key.SERVICE_ID] = client_service[Key.SERVICE_ID]
            payload[Key.SERVICE_NAME] = client_service[Key.SERVICE_NAME]
            payload[Key.SERVICE_DISPLAY_NAME] = client_service[Key.SERVICE_DISPLAY_NAME]
            payload[Key.REQUEST_HOST] = client_service[Key.REQUEST_HOST]

        if host_url:
            payload[Key.HOST_URL] = host_url

        try:
            private_key = self.token_config[Token.PRIVATE_KEY]
            token = jwt.encode(payload, private_key, algorithm=self.token_config[Token.ALGORITHM])
        except Exception as e:
            print(str(e))
            raise RuntimeError(f"Error encountered while generating token {_print}")
        
        if token:
            print(f"Token {_print}:{token}")
            return token
        else:
            raise RuntimeError(f"Could not generate token {_print}")



    def validate():
        pass
