import logging

from flask import Flask, redirect, url_for, request
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError

from extensions import csrf
from models import db, security, user_datastore
from views import views
from utils import list_obj_stringify
from admin import admin
from config import BaseConfig

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
db.init_app(app)
security_state = security.init_app(app, user_datastore)
security._state = security_state
csrf.init_app(app)
admin.init_app(app)

#Migartion Part
"""Needs to add in migrations/env.py in context.configure
after flask db init: render_as_batch=True,
to enable sqlite droping tables"""
migrate = Migrate(app, db)

#registering views and APIs
app.register_blueprint(views)

#Creating a 404 template
@app.errorhandler(404)
def not_found(error):
    return redirect('/')

#Handling CSRF errors
@app.errorhandler(CSRFError)
def csrf_error(reason):
    flash('You have been logged out. Please login again!')
    return redirect(url_for('security.logout'))

#registering Jinja Filters
app.jinja_env.filters['list_obj_stringify'] = list_obj_stringify

# Logging section
fileHandler = logging.FileHandler(BaseConfig.GLOBAL_LOG_FILE)
fileHandler.setFormatter(
    logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
)
app.logger.propagate = False
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(fileHandler)
@app.before_request
def logg_request():
    app.logger.debug('%s - %s' % (request.remote_addr, request.url))

if __name__ == "__main__":
    app.run(debug=True)