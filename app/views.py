# -*- coding: utf-8 -*-

import os
import requests
import werkzeug

from flask.ext.restful import (Resource, reqparse, abort)
from PIL import Image
from itsdangerous import (BadSignature, SignatureExpired)
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.apps import custom_app_context as pwd_context

from . import db
from .config import SECRET_KEY, UPLOAD_FOLDER
from .errors import unauthorized


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String(32), index=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(64))
    logo = db.Column(db.LargeBinary(100))
    tel = db.Column(db.String(32))
    email = db.Column(db.String(32))
    address = db.Column(db.String(128))
    nickname = db.Column(db.String(64))

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user


class Register(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username could not convert')
        parser.add_argument('password', type=str, help='password could not counvert')
        args = parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        if username is None or password is None:
            abort(400)
        if User.query.filter_by(username=username).first() is not None:
            abort(400)
        if len(username) < 6:
            abort(410)

        users = User.query.all()

        user = User(username=username)
        user.hash_password(password)
        user.cid = len(users) ^ 5405336615

        db.session.add(user)
        db.session.commit()
        token = user.generate_auth_token(600)
        return {'username': user.username, 'token': token.decode('ascii')}, 1

    def get(self):
        r = requests.get('https://github.com/timeline.json')
        return {'result': r.content}


class Login(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username could not convert')
        parser.add_argument('password', type=str, help='password could not convert')
        args = parser.parse_args()
        username = args.get('username')
        password = args.get('password')

        user = User.query.filter_by(username=username).first()
        if user is None:
            return {'msg': 'user is not found'}
        if user.verify_password(password):
            token = user.generate_auth_token(600)
            return {'token': token.decode('ascii')}


class Profile(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, help='access_token could not convert')
        parser.add_argument('logo', type=werkzeug.datastructures.FileStorage, location='files')

        args = parser.parse_args()

        logo = args.get('logo')
        access_token = args.get('access_token')

        if access_token is None or User.verify_auth_token(access_token) is None:
            return unauthorized(u'还没有登陆哦~'.encode('utf-8'))

        user = User.verify_auth_token(access_token)

        image = Image.open(logo.stream)
        filename = user.cid + '.png'
        path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(path)

        return {'msg': 'success'}
