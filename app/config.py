import os

SECRET_KEY = 'the application of peanuts'
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True


UPLOAD_FOLDER = os.path.dirname(os.path.abspath('__file__')) + '/uploads'


EASE_MOB_APP_ENTERPRISE = 'oenius'
EASE_MOB_APP_NAME = 'peanuts'
EASE_MOB_APP_SECRET_KEY = 'YXA6aqrA6UXgPLcKCUI7EBDjeZ7TcP4'
