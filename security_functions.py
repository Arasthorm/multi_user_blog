import hashlib	
import hmac
import random
import string

import database_functions as d_func

SECRET = "imasecret"

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):

    """
    Hashes the value of the cookie in order to check for tampering

    Args:
        s : value to be hashed

    Returns:
            a string composed by the original value and the hmac of the value + some secret

    """


    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


def make_salt(n):
    return "".join([random.choice(string.letters) for x in range(0, n)])


def secure_pass(name, password, n):

    """
    Enables a more secure password storing

    Args:
        name : The username provided
        password : The password provided
        n : An integer that defines the size of the salt

    Returns:
            A hash using sha256 of name + password + salt

    """


    salt = make_salt(n)
    h = hashlib.sha256(name+password+salt).hexdigest()
    return "%s|%s" % (h, salt)


def verify_pass(name, password, h):

    salt = h.split("|")[1]
    hashed = hashlib.sha256(name+password+salt).hexdigest()
    my_h = '%s|%s' % (hashed, salt)
    
    return True if h == my_h else False


def read_secure_cookie(self):

    username_cookies_str = self.request.cookies.get('user_id')

    if username_cookies_str and not username_cookies_str == "" and not username_cookies_str == None:
        
        cookie_val = check_secure_val(username_cookies_str)
        if cookie_val:
            user_id = cookie_val
            return user_id
    else:
        return ""



def set_secure_cookie(self, user_id):

    """
    Defines a cookie with the field user_id as the id generated to the current user

    Args:
        user_id : Id generated to the current user

    """

    new_cookie_val = make_secure_val(user_id)
    self.response.headers.add_header(
        "Set-Cookie", 'user_id=%s; path=/;' % new_cookie_val)











