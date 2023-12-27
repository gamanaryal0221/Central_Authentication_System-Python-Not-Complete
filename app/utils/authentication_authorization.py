import random
import string
import hashlib
import re

from .constants import Key
from .common import get_count_from_cursor


class Password():

    entered_password = None

    def __init__(self, raw_password):
        print("\nInitializing password ...")
        if raw_password:
            self.entered_password = raw_password
        else:
            raise RuntimeError("Provided password is null")
        
    def check_validity(self):
        messages = []
        message = ""

        length_of_password = len(self.entered_password)
        if (length_of_password<8 and length_of_password>12):
            message = f"Password must be atleast 8-12 character long"

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', self.entered_password):
            messages.append("one uppercase letter")

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', self.entered_password):
            messages.append("one lowercase letter")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\|]', self.entered_password):
            messages.append("one special character")

        # Check for at least one number
        if not re.search(r'\d', self.entered_password):
            messages.append("one number")


        if messages:
            message = f"{message} and contain at least " if message else "Password must contain at least "

            last_message_index = len(messages) - 1
            for i, msg in enumerate(messages):
                message = message + (msg if i is 0 else (f", and {msg}" if i==last_message_index else f", {msg}"))
        

        return f"{message}." if message else None
        

    def _generate_salt_value(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(10))
    
    def _hash_entered_password(self, salt_value):
        print("password hashing ...")
        hashed_password = None
        try:
            if salt_value is not None and self.entered_password is not None:
                hashed_password = hashlib.sha512((salt_value + self.entered_password).encode()).hexdigest()
            else:
                print("Salt value or password is null")
        except Exception as e:
            print(f"Error encountered while password hashing: {e}")
    
        return hashed_password

    def make(self):
        print("Creating password ...")
        salt_value = self._generate_salt_value()
        hashed_password = self._hash_entered_password(salt_value)
        return {Key.SALT_VALUE:salt_value, Key.HASHED_PASSWORD:hashed_password}

    def is_correct(self, stored_password_detail):
        print("Validating password ...")
        if stored_password_detail:
            entered_password_hash = self._hash_entered_password(stored_password_detail[Key.SALT_VALUE])
            stored_password_hash = stored_password_detail[Key.HASHED_PASSWORD]

            if entered_password_hash == stored_password_hash:
                print("passord matched successfully")
                return True
            else:
                print("Password did not match")
                return False
        else:
            raise RuntimeError("Stored password detail is null")
        


class Access():
    def is_valid_for_respective_client_service(conn, user, client_service):
        print(f"Validating access of user[id:{user[Key.USER_ID]}] on client_service[id:{client_service[Key.CLIENT_SERVICE_ID]}] ...")
        cursor = conn.cursor()
        cursor.execute(
            f"select count(*) from user_client_service ucs "+
            "where ucs.user_id = %s and ucs.client_service_id = %s ",
            [user[Key.USER_ID], client_service[Key.CLIENT_SERVICE_ID]]
        )

        count = get_count_from_cursor(cursor)
        cursor.close()

        return (count > 0)