from .common import get_request_host, get_mapped_records
from .constants import Key
        

def get_connection(self, data_source_key):
    if data_source_key:
        mysql_connections = self.application.mysql_connections
        if data_source_key in mysql_connections:
            return mysql_connections[data_source_key]
        else:
            raise RuntimeError(f"Could not find connection with '{data_source_key}'")
    else:
        raise ValueError("Null data source key received")


def get_client_and_service_details_from_hosturl(conn, host_url):
    request_host = get_request_host(host_url)
    if not request_host: return None

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


def get_user_detail(conn, username):
    cursor = conn.cursor()
    cursor.execute(
        f"select u.id as {Key.USER_ID}, ue.email as {Key.EMAIL}, un.number as {Key.NUMBER}, "+
        f"u.first_name as {Key.FIRST_NAME}, u.middle_name as {Key.MIDDLE_NAME}, u.last_name as {Key.LAST_NAME}, "+
        f"u.salt_value as {Key.SALT_VALUE}, u.password as {Key.HASHED_PASSWORD} "
        "from user u "+
        "inner join user_email ue on ue.user_id=u.id "+
        "inner join user_number un on un.user_id=u.id "+
        "where ue.is_primary=true and un.is_primary=true "+
        "and (ue.email = %s or un.number = %s or u.username = %s)", 
        [username, username, username]
    )
    user = get_mapped_records(cursor)
    print(f"user:{user}")
    return user

