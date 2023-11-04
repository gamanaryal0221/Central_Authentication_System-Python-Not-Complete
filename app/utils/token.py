import datetime
import jwt

from enum import Enum
from .constants import Config, Key, Token

from .custom_exceptions import NotFoundInApplicationException
from .common import get_request_host
from .db_utils import get_count_of_password_reset_using_token

class JwtToken():
    
    class Purpose(Enum):
        LOGIN_SUCCESSFUL = "vcp.token.jwt.login.successful"
        RESET_PASSWORD = "vcp.token.jwt.forgot_password.reset"

    token_config = None
    purpose:Purpose = None

    def __init__(self, _self, _purpose:Purpose):
        print(f"\nInitializing token generation ...")
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


    def generate(self, user, client_service, host_url, connection=None):
        _print = f"'{self.purpose.value}' for user[id:{user[Key.USER_ID]}]"
        print(f"Generating token {_print} ...")

        payload = {
            Key.TOKEN_PURPOSE: self.purpose.value,
            Key.USER_ID: user[Key.USER_ID],
            Key.EXPIRE: datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_config[Token.EXPIRE_DURATION])
        }

        if self.purpose is self.Purpose.RESET_PASSWORD:
            previous_count_of_password_changed_using_token = get_count_of_password_reset_using_token(connection, user[Key.USER_ID])
            payload[Key.CURRENT_COUNT_OF_PASSWORD_RESET_REQUEST_USING_TOKEN] = previous_count_of_password_changed_using_token + 1
        else:

            payload[Key.EMAIL] = user[Key.EMAIL],
            payload[Key.USERNAME] = user[Key.USERNAME],
            payload[Key.NUMBER] = user[Key.NUMBER],
            payload[Key.FULLNAME] = f"{user[Key.FIRST_NAME]}{' '+user[Key.MIDDLE_NAME] if user[Key.MIDDLE_NAME] else ''} {user[Key.LAST_NAME]}",

            if client_service:
                payload[Key.CLIENT_ID] = client_service[Key.CLIENT_ID]
                payload[Key.CLIENT_NAME] = client_service[Key.CLIENT_NAME]
                payload[Key.SERVICE_ID] = client_service[Key.SERVICE_ID]
                payload[Key.SERVICE_NAME] = client_service[Key.SERVICE_NAME]
                payload[Key.SERVICE_DISPLAY_NAME] = client_service[Key.SERVICE_DISPLAY_NAME]
                payload[Key.REQUEST_HOST] = client_service[Key.REQUEST_HOST]

            if host_url:
                payload[Key.HOST_URL] = host_url
                if Key.REQUEST_HOST not in payload:
                    payload[Key.REQUEST_HOST] = get_request_host(host_url)

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


    def validate(self, token):
        print("\nValidating token ...")

        response = {}

        is_validated = False
        is_forbidden = None
        title = None
        message = None

        if token:

            payload = None

            try:
                print(f"token: {token}")
                payload = jwt.decode(token, self.token_config[Token.PRIVATE_KEY], algorithms=[self.token_config[Token.ALGORITHM]])

                print(f"payload: {payload}")
                if payload:

                    purpose_of_token = payload[Key.TOKEN_PURPOSE]
                    
                    print(f"Purpose of token [should be:'{purpose_of_token}', decoded:'{purpose_of_token}'")

                    if (purpose_of_token == self.purpose.value):

                        if purpose_of_token == self.Purpose.RESET_PASSWORD.value:
                            if Key.CURRENT_COUNT_OF_PASSWORD_RESET_REQUEST_USING_TOKEN in payload:
                                is_validated = True
                                response[Key.PAYLOAD] = payload
                            else:
                                message = "Some essential attributes are missing in the token.\nPlease contact your administrator"     
                        else:
                            is_validated = True
                            response[Key.PAYLOAD] = payload
                    else:
                        is_forbidden = True
                        print("The purpose of token is invalid")
                        message = "Invalid token"
                else:
                    message = "Decoded payload is null"

            except jwt.ExpiredSignatureError as ese:
                print(ese)
                is_forbidden = True
                message = "Token has been expired"
                    
            except jwt.InvalidTokenError as ite:
                print(ite)
                is_forbidden = True
                message = "Invalid token"

            except Exception as e:
                is_forbidden = True
                message = f"Error encountered on validating token {e}"

        else:
            message = "Missing token"

        response[Key.IS_VALIDATED] = is_validated
        response[Key.IS_FORBIDDEN] = title
        response[Key.MESSAGE] =  message
        print(f"Token validation response:{response}")

        return response
