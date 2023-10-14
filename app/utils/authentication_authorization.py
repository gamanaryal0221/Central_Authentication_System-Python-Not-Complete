import bcrypt

from .constants import Key
from app import settings


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