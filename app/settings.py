from os import getenv

APP_NAME = 'referees'
# Default to info
LOG_LEVEL = getenv("LOG_LEVEL") or 20

SQLALCHEMY_URI = getenv("SQLALCHEMY_URI")
SQLALCHEMY_DATABASE_URI = SQLALCHEMY_URI

SECRET_KEY = getenv('SECRET_KEY', 'my_secret')
SECRET_TIMEOUT = int(getenv('SECRET_TIMEOUT', '900'))
DEBUG = getenv('DEBUG', False)
TESTING = getenv('TESTING', False)
BCRYPT_LOG_ROUNDS = 13

# Flask-security settings
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = getenv('PASSWORD_SALT') or 'mySalt'
SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
SECURITY_TOKEN_MAX_AGE = 1800
SECURITY_TRACKABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CONFIRMABLE = False
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_USER_IDENTITY_ATTRIBUTES = 'email'
SECURITY_LOGIN_URL = '/login'
WTF_CSRF_ENABLED = False

# Email
MAIL_SERVER = getenv('MAIL_SERVER', 'smtp.sendgrid.net')
MAIL_PORT = int(getenv('MAIL_PORT', '587'))
MAIL_USE_TLS = getenv('MAIL_USE_TLS', True)
MAIL_USE_SSL = getenv('MAIL_USE_SSL', False)
MAIL_USERNAME = getenv('MAIL_USERNAME')
MAIL_PASSWORD = getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = getenv('MAIL_DEFAULT_SENDER')

# Admin account
ADMIN_PASSWORD = getenv('ADMIN_PASSWORD', 'password123#')
ADMIN_EMAIL = getenv('ADMIN_EMAIL', 'admin@example.com')
EMAIL_SUBJECT_PREFIX = f"[{APP_NAME}]"
EMAIL_SENDER = f"{APP_NAME} Admin <{MAIL_USERNAME}>"

SOCIAL_GOOGLE = {
    'consumer_key': "cute.apps.googleusercontent.com",
    'consumer_secret': "password"
}

GRAPHIQL = getenv('GRAPHIQL', False)
