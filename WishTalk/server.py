# -*- coding: utf-8 -*-

from base64 import b64encode
from config import DEBUG, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_COMMIT_ON_TEARDOWN, REDIS_PORT, REDIS_DB
from gevent.wsgi import WSGIServer
from uuid import uuid4
from flask import redirect, url_for
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import redis


class App(object):
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = b64encode(uuid4().hex)
        self.app.debug = DEBUG
        self.app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
        self.app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        self.app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = SQLALCHEMY_COMMIT_ON_TEARDOWN

    def register_api_blueprint(self):
        from api import api
        self.app.register_blueprint(api, url_prefix='/api')

    def register_admin_blueprint(self):
        from admin import admin
        self.app.register_blueprint(admin, url_prefix='/admin')

    def run(self):
        self.register_api_blueprint()
        self.register_admin_blueprint()
        if DEBUG:
            from config import DEBUG_IP, DEBUG_PORT
            self.app.debug = True
            self.app.run(host=DEBUG_IP, port=DEBUG_PORT)
        else:
            from config import NONDEBUG_IP, NONDEBUG_PORT
            self.app.debug = False
            self.app.run(host=NONDEBUG_IP, port=NONDEBUG_PORT)


app = App()
db = SQLAlchemy(app.app)
redisClient = redis.Redis(host='127.0.0.1', port=REDIS_PORT, db=REDIS_DB)


@app.app.route('/', methods=["GET"])
def index():
    return redirect('/admin/')

if __name__ == '__main__':
    app.run()
