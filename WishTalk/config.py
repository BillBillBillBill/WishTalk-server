# -*- coding: utf-8 -*-

HOSTNAME = 'localhost:8080'

DEBUG = True

DEBUG_IP = 'localhost'
DEBUG_PORT = 5000

NONDEBUG_IP = '0.0.0.0'
NONDEBUG_PORT = 5000

DB_USERNAME = 'root'   # 数据库用户名
DB_PASSWORD = ''       # 数据库密码
DB_PORT = 3306         # 数据库端口
DB_NAME = 'wishtalk'         # 数据库名称

REDIS_PORT = 6379
REDIS_DB = 0

SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@localhost:%d/%s?charset=utf8&use_unicode=0' % (DB_USERNAME, DB_PASSWORD, DB_PORT, DB_NAME)

SQLALCHEMY_COMMIT_ON_TEARDOWN = True

UPLOAD_PATH = 'uploads/'

SMS_APPID = "23284008"
SMS_APPKEY = "9411c36dbf137d7ddf8d89da556ae906"

RC_APPKEY = "bmdehs6pdwa3s"
RC_APPSECRET = "V3izbHVnqu"
