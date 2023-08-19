class Template():
    LOGIN = "login.html"
    ERROR = "error.html"
    FORGOT_PASSWORD = "forgot_password.html"


class Environment():
    KEY = "environment"
    DEVELOPMENT = "dev"
    QC = "qc"
    PROD = "prod"

class Key():
    HOST_URL = "host_url"
    REQUEST_HOST = "request_host"

    SECRET_COOKIE_KEY = "cookie_secret"

    STATUS_CODE = "status_code"
    TITLE = "title"
    MESSAGE = "message"
    REDIRECT_URL = "redirect_url"
    REDIRECT_TEXT = "redirect_text"

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
    EXPIRE_ON = "exp"
    
    TOKEN = "token"

    ERROR_MSG = "error_msg"


class Config():
    MYSQL_DATA_SOURCES = "data_sources"


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