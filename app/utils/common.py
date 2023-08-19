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
    request_host = str(host_url).replace("http://","").replace("https://","")
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