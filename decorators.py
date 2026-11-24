from flask import session, redirect, url_for
from functools import wraps


def login_reqired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return "null"
        return f(*args, **kwargs)
    return wrapper