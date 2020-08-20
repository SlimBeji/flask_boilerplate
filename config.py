import os
filedir = os.path.dirname(__file__)

class BaseConfig:
    #Global Parameters
    SECRET_KEY = 'This_is_supposed_to_be_a_secret_key'
    GLOBAL_LOG_FILE = os.path.join(filedir, 'log', 'flask.log')

    #Database Parametetrs
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(filedir, 'api.db')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Flask-Security config
    SECURITY_POST_LOGOUT_VIEW = '/login'
    SECURITY_DEFAULT_REMEMBER_ME = True
    SECURITY_REMEMBER_SALT = 'A2ABCF289ECFBC18C1E91FDCA92C9'
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"
    SECURITY_FLASH_MESSAGES = True
    SECURITY_REGISTERABLE = False
