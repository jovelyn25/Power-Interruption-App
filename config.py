MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'youremail@gmail.com'
MAIL_PASSWORD = 'your_app_password'  # Use app password, not your Gmail login
MAIL_DEFAULT_SENDER = 'youremail@gmail.com'

SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/requests.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional but recommended
