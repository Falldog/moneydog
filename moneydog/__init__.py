# Import the Flask Framework
from flask import Flask

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
from moneydog import urls
from moneydog import views
from moneydog import views_admin
from moneydog import filters


