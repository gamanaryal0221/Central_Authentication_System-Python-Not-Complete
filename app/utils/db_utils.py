from .common import get_request_host, get_mapped_records, get_count_from_cursor
from .constants import Config, Key
from .custom_exceptions import NotFoundInApplicationException
        

def get_connection(_self, server):
    if server:
        mysql_connections = _self.application.config[Config.MYSQL]
        if server in mysql_connections:
            return mysql_connections[server]
        else:
            raise RuntimeError(f"Could not find connection with '{server}'")
    else:
        raise NotFoundInApplicationException(f" {server} in {Config.MYSQL}")


def get_client_and_service_details_from_hosturl_or_request_host(conn, host_url, request_host):
    request_host = request_host if request_host else get_request_host(host_url)
    if not request_host or request_host is None: return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            f"select c.id as {Key.CLIENT_ID}, c.name as {Key.CLIENT_NAME}, c.display_name as {Key.CLIENT_DISPLAY_NAME}, "+
            f"c.is_google_authentication_enabled as {Key.IS_GOOGLE_AUTHENTICATION_ENABLED}, c.is_credential_authentication_enabled as {Key.IS_CREDENTIAL_AUTHENTICATION_ENABLED}, "
            f"s.id as {Key.SERVICE_ID}, s.name as {Key.SERVICE_NAME}, s.display_name as {Key.SERVICE_DISPLAY_NAME}, "+
            f"cs.id as {Key.CLIENT_SERVICE_ID}, cs.request_host as {Key.REQUEST_HOST} "
            "from client_service cs "+
            "inner join client c on c.id=cs.client_id "+
            "inner join service s on s.id=cs.service_id "+
            "where c.soft_deleted=false and s.soft_deleted=false "
            "and cs.request_host = %s ",
            [request_host]
        )
        client_service = get_mapped_records(cursor)
        print(f"client_service:{client_service}")
        return client_service
    except Exception as e:
        print(f"Error encountered while fetching client ans service details from hosturl or request host: {e}")
        return None


def get_user_detail_by_email_username_or_number(conn, username, include_password_details = False):
    return _get_user_detail(conn, None, username, include_password_details)

def get_user_detail_by_id(conn, user_id, include_password_details = False):
    return _get_user_detail(conn, user_id, None, include_password_details)

def _get_user_detail(conn, user_id, username, include_password_details = False):
    plus_sql = "and (ue.email = %s or un.number = %s or u.username = %s)" if username else "and u.id = %s "
    params = [username, username, username] if username else [user_id]
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"select u.id as {Key.USER_ID}, ue.email as {Key.EMAIL}, un.number as {Key.NUMBER}, u.username as {Key.USERNAME}, "+
            f"u.first_name as {Key.FIRST_NAME}, u.middle_name as {Key.MIDDLE_NAME}, u.last_name as {Key.LAST_NAME} "+
            (f", u.salt_value as {Key.SALT_VALUE}, u.password as {Key.HASHED_PASSWORD} " if include_password_details else "") +
            "from user u "+
            "inner join user_email ue on ue.user_id=u.id "+
            "inner join user_number un on un.user_id=u.id "+
            "where ue.is_primary=true and un.is_primary=true "+
            plus_sql, 
            params
        )
        user = get_mapped_records(cursor)
        print(f"user:{user}")
        return user
    except Exception as e:
        print(f"Error encountered while fetching user detail by {'email username or number' if username else 'user id'}: {e}")
        return None


def get_count_of_password_reset_using_token(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        f"select count(*) from user_password_history "+
        "where user_id = %s and is_reset_using_token = %s ", 
        [user_id, True]
    )
    
    return get_count_from_cursor(cursor)


def update_password_of_a_user(conn, user_id, hashed_password_detail):
    salt_value = hashed_password_detail[Key.SALT_VALUE]
    hashed_password = hashed_password_detail[Key.HASHED_PASSWORD]

    if salt_value and hashed_password:

        try:
            cursor = conn.cursor()
            cursor.execute(
                "update user u "+
                "set u.salt_value = %s, u.password = %s "+
                "where u.id = %s ", 
                [salt_value, hashed_password, user_id]
            )

            rows_affected = cursor.rowcount
            if (rows_affected > 0):
                conn.commit()

                # inserting into user_password_history_record
                cursor = conn.cursor()
                cursor.execute(
                    "insert into user_password_history(user_id, salt_value, password, is_reset_using_token) " +
                    "values (%s, %s, %s, %s); ", 
                    [user_id, salt_value, hashed_password, True]
                )
                conn.commit()

                return True
            else:
                return False
        except Exception as e:
            print(f"Error encountered while updating password: {e}")
            return False
    else:
        raise RuntimeError(f"Salt value or password is null [salt_value:{salt_value}, hashed_password:{hashed_password}]")