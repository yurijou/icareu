from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Api


db = SQLAlchemy()
auth = HTTPBasicAuth()


def register_apis(app):
    from .views import (Register, Login, Profile)
    from flask import render_template
    api = Api(app)
    api.add_resource(Register, '/v1/regiter', endpoint='register')
    api.add_resource(Login, '/v1/login', endpoint='login')
    api.add_resource(Profile, '/v1/profile', endpoint='profile')
    @app.route('/')
    def hello_world():
    	return render_template('index.html')


def create_app():
    app = Flask(__name__)
    db.init_app(app)

    register_apis(app)

    app.config.from_object(config)
    return app

from app import views
