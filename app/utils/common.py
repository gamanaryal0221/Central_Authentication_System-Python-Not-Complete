from urllib.parse import urlparse
import traceback

from app.utils.constants import Key, Template

def render_error_page(self, status_code=504, title="Technical Error", message="Something went wrong\nPlease try again", redirect_url = None, redirect_text = None):
    error =  {"error":{
        Key.STATUS_CODE: status_code,
        Key.TITLE: title,
        Key.MESSAGE: message,
        Key.REDIRECT_URL: redirect_url,
        Key.REDIRECT_TEXT: redirect_text
    }}

    self.render(Template.ERROR, **error)

def get_request_host(host_url):
    request_host = None
    try:
        # Parse the URL
        parsed_url = urlparse(host_url)

        # Extract the netloc, which contains the domain (i.e. request_host)
        request_host = parsed_url.netloc
    except:
        traceback.print_exception()
    print(f"request_host:{request_host} from host_url:{host_url}")
    return request_host


def get_mapped_records(cursor, want_one_if_one=True):
    if cursor.rowcount > 0:
        all_data = cursor.fetchall()
        # print(f"all_data:{all_data}")

        records = []
        columns = [column[0] for column in cursor.description]
        # print(f"columns:{columns}")

        for data in all_data:
            # print(f"data:{data}")
            record = dict(zip(columns, data))
            # print(f"record:{record}")
            records.append(record)

        if len(records)==1 and want_one_if_one:
            return records[0]
        else:
            return records
    else:
        None

def get_count_from_cursor(cursor):
    all_data = cursor.fetchall()
    if all_data:
        first_record = all_data[0]
        if first_record:
            return first_record[0] if first_record[0] else 0
        else:
            return 0
    else:
        return 0

def fetch_data(_from, key, default_value=None):
    print(f"Reading '{key}' ...")
    if key in _from:
        return _from[key]
    else:
        if default_value:
            print(f"Missing configuration for '{key}' -> Putting {default_value} as default value")
            return default_value
        else:
            raise ImportError(f"Missing configuration for '{key}'")
        

def login_succes_redirect_to_application(_self, request_host, host_url, token):
    print("\nRedirecting to application ...")

    if request_host or host_url:
        redirection_url = ("https://" if "https://" in host_url else "http://") if host_url else "https://"
        
        request_host = (request_host if request_host else get_request_host(host_url))
        redirection_url = redirection_url + request_host

        redirection_url = redirection_url + f"/login/success?host_url={host_url}&token={token}"
        print(f"Redirecting to {redirection_url}")
        _self.redirect(f"{redirection_url}")
    else:
        raise RuntimeError(f"Invalid [request_host:{request_host}, host_url:{host_url}]")