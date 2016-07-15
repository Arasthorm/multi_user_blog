import re

import database_functions as d_func


def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return True if USER_RE.match(username) else False 

def valid_password(password):
    PASS_RE = re.compile(r"^.{3,20}$")
    return True if PASS_RE.match(password) else False

def valid_validation(password, verify):
    if not password == verify:
        return False
    return True


def valid_email(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return True if EMAIL_RE.match(email) else False

def already_exists_username(username):

    creds = d_func.Credentials.get_all_credentials()

    for c in creds:
        if c.username == username:
            return True
    return False


