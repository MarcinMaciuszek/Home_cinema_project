class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    FLASK_ADMIN_SWATCH = 'superhero'
    SECRET_KEY = 'secret_key'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = 'password_salt'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kinotest@gmail.com' # should be replaced by correct email
    # generated password after enable 2-step verification
    MAIL_PASSWORD = 'kino_password' # should be replaced by correct email password
    MAIL_DEFAULT_SENDER = 'kinotest@gmail.com' # should be replaced by correct email