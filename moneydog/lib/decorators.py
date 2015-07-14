from google.appengine.api import users
from functools import wraps
import flask
from flask import abort, redirect, url_for

from datetime import date


def login_required(func, redirect_url='/'):
    @wraps(func)
    def new_func(*argv, **argd):
        user = users.get_current_user()
        if user:
            return func(*argv, **argd)
        else:
            return redirect(users.create_login_url(redirect_url))
    return new_func


def update_basic_context(func):
    @wraps(func)
    def new_func(*argv, **argd):
        y = date.today().year

        flask.g.logout_url = users.create_logout_url('/')
        flask.g.year_range = range(y-10, y+1)

        return func(*argv, **argd)
    return new_func

