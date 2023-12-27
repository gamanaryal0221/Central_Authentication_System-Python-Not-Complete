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

def get_splitted_url(host_url):
    request_host = None
    try:
        parsed_url = urlparse(host_url)
        return {Key.REQUEST_HOST: parsed_url.hostname, Key.FULL_REQUEST_HOST: parsed_url.netloc}
    except Exception as e:
        traceback.print_exception(e)
    print(f"request_host:{request_host} from host_url:{host_url}")
    return request_host

def get_mapped_record(cursor):
    return get_mapped_records(cursor, False)

def get_mapped_records(cursor, return_in_list=True):
    if cursor.rowcount > 0:
        all_data = cursor.fetchall()

        records = []
        columns = [column[0] for column in cursor.description]

        for data in all_data:
            record = dict(zip(columns, data))
            records.append(record)

        if len(records)==1:
            if return_in_list:
                return records
            else:
                return records[0]
        else:
            return records
    else:
        []

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
            print(f"Missing value for '{key}' -> Putting {default_value} as default value")
            return default_value
        else:
            raise Exception(f"Missing configuration for '{key}'")