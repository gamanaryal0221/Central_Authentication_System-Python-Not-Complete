import bcrypt
import datetime
import jwt

from .constants import Key
from app import settings


class TokenDetail():
    private_key = None
    expire_duration = None #in hours
    algorithm = None

class Token():
    def generate_and_redirect(self, user, client_service, host_url):

        token_detail = self.application.token_detail
        if token_detail:

            payload = {
                Key.USER_ID: user[Key.USER_ID],
                Key.EMAIL: user[Key.EMAIL],
                Key.NUMBER: user[Key.NUMBER],
                Key.FULLNAME: f"{user[Key.FIRST_NAME]}{' '+user[Key.MIDDLE_NAME] if user[Key.MIDDLE_NAME] else ''} {user[Key.LAST_NAME]}",
                Key.CLIENT_ID: client_service[Key.CLIENT_ID],
                Key.CLIENT_NAME: client_service[Key.CLIENT_NAME],
                Key.SERVICE_ID: client_service[Key.SERVICE_ID],
                Key.SERVICE_NAME: client_service[Key.SERVICE_NAME],
                Key.SERVICE_DISPLAY_NAME: client_service[Key.SERVICE_DISPLAY_NAME],
                Key.REQUEST_HOST: client_service[Key.REQUEST_HOST],
                Key.HOST_URL: host_url,
                Key.EXPIRE_ON: datetime.datetime.utcnow() + datetime.timedelta(hours=token_detail.expire_duration)
            }

            # Generating the JWT token
            try:
                private_key = token_detail.private_key
                token = jwt.encode(payload, private_key, algorithm=token_detail.algorithm)
                print(f'\nGenerated Token for user[id:{user[Key.USER_ID]}]:', token, '\n')

            except Exception as e:
                print(str(e))
                raise RuntimeError("Error encountered while generating token")
            
            if token:
                redirection_url = ("https://" if "https://" in host_url else "http://") + client_service[Key.REQUEST_HOST] + f"/login/success?host_url={host_url}&token={token}"
                print(f"Login successful for user[id:{user[Key.USER_ID]}]")
                print(f"Redirecting to {redirection_url}")
                self.redirect(f"{redirection_url}")
            else:
                raise RuntimeError("Could not generate token")
        else:
            raise RuntimeError("Received null token detail from application")


class Password():

    def is_valid(stored_password_detail, provided_password):
        print("Validating password ...")
        if stored_password_detail and provided_password:
            stored_salt = stored_password_detail[Key.SALT_VALUE]
            stored_hashed_password = stored_password_detail[Key.HASHED_PASSWORD]

            return stored_hashed_password.encode(settings.PASSWORD_ENCODING_STANDARD) == bcrypt.hashpw(provided_password.encode(settings.PASSWORD_ENCODING_STANDARD), stored_salt.encode(settings.PASSWORD_ENCODING_STANDARD))
        else:
            raise RuntimeError("Stored password detail or provided password is null")
        


class Access():
    def is_valid_for_respective_client_service(conn, user, client_service):
        print(f"Validating access of user[id:{user[Key.USER_ID]}] on request_host:{client_service[Key.REQUEST_HOST]}")
        cursor = conn.cursor()
        cursor.execute(
            f"select * from user_client_service ucs "+
            "where ucs.user_id = %s and ucs.client_service_id = %s ",
            [user[Key.USER_ID], client_service[Key.CLIENT_SERVICE_ID]]
        )

        return (cursor.rowcount > 0)