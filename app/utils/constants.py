class Template():
    LOGIN = "login.html"
    ERROR = "error.html"
    FORGOT_PASSWORD = "forgot_password.html"
    RESET_PASSWORD = "reset_password.html"


class Environment():
    KEY = "environment"
    DEVELOPMENT = "dev"
    QC = "qc"
    PRODUCTION = "prod"

class Key():
    PORT = "port"

    HOST_URL = "host_url"
    REQUEST_HOST = "request_host"

    SECRET_COOKIE_KEY = "cookie_secret"

    STATUS_CODE = "status_code"
    TITLE = "title"
    MESSAGE = "message"
    REDIRECT_URL = "redirect_url"
    REDIRECT_TEXT = "redirect_text"

    IS_VALIDATED = "is_validated"
    PAYLOAD = "payload"

    CLIENT_ID = "client_id"
    CLIENT_NAME = "client_name"
    CLIENT_DISPLAY_NAME = "client_display_name"
    IS_GOOGLE_AUTHENTICATION_ENABLED = "is_google_authentication_enabled"
    IS_CREDENTIAL_AUTHENTICATION_ENABLED = "is_credential_authentication_enabled"

    SERVICE_ID = "service_id"
    SERVICE_NAME = "service_name"
    SERVICE_DISPLAY_NAME = "service_display_name"

    CLIENT_SERVICE_ID = "client_service_id"

    CLIENT_LOGO_URL = "client_logo_url"
    BACKGROUND_IMAGE_URL = "background_image_url"

    USERNAME = "username"
    PASSWORD = "password"
    CONFIRM_PASSWORD = "confirm_password"
    
    SALT_VALUE = "salt_value"
    HASHED_PASSWORD = "hashed_password"

    USER_ID = "user_id"
    FIRST_NAME = "first_name"
    MIDDLE_NAME = "middle_name"
    LAST_NAME = "last_name"
    FULLNAME = "fullname"
    GENDER = "gender"
    EMAIL = "email"
    NUMBER = "number"
    EXPIRE = "exp"
    
    TOKEN = "token"
    SMTP = "smtp"

    STATUS_MSG = "status_msg"
    STATUS_MSG_COLOR = "status_msg_color"

    TOKEN_PURPOSE = "token_purpose"
    CURRENT_COUNT_OF_PASSWORD_RESET_REQUEST_USING_TOKEN = "current_count_of_password_reset_request_using_token"
    IS_FORBIDDEN = "is_forbidden"


class Config():
    # All the main keys mentioned in config file and will be further stored in application property will be listed here
    MYSQL = "mysql"
    TOKEN = "token"
    SMTP = "smtp"


class Mysql():
    RESOURCE_MANAGER = "resource_manager"

    HOSTNAME = "hostname"
    DATABASE = "database"
    USER = "user"
    PASSWORD = "password"


class Token():
    PRIVATE_KEY = "private_key"
    EXPIRE_DURATION = "expire_duration"
    ALGORITHM = "algorithm"

    DEFAULT_EXPIRE_DURATION = 8
    DEFAULT_ALGORITHM = 'HS256'


class SMTP():
    SERVER = "server"
    PORT = "port"
    USERNAME = "username"
    PASSWORD = "password"

    SENDER_EMAIL = 'sender_email'

class Default():
    STATUS_MSG_COLOR = "red"
    COMPANY_NAME = "Virtual Corp"


class Url():
    CAS_RESET_PASSWORD_URL = f"http://login.{Environment.KEY.upper()}.vcp.com/reset-password?token={Key.TOKEN.upper()}"