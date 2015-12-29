# -*- coding: utf-8 -*-

from api import GlobalError
from jsonResponse import jsonError
from functools import wraps
from server import redisClient, db
from flask import request
from model.user import User

def token_required(func):
    '''check token required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        # 将ImmutableMultiDict变成Dict类型
        request.args = request.args.to_dict()
        # 如果值为空字符串 删掉对应的键 否则后面的request.args.get()会出问题
        for k, v in request.args.items():
            if v == '':
                request.args.pop(k)
        # print request.args
        token = request.args.get('token', None) or request.form.get('token', None)
        if not token:
            if request.json == None:
                return jsonError(GlobalError.TOKEN_VALIFY_FAILED), 401
            else:
                token = request.json.get('token', None)
                if not token:
                    return jsonError(GlobalError.TOKEN_VALIFY_FAILED), 401
        try:
            if len(token.split('$')) == 4:
                userid = token.split('$')[1]
                if redisClient.get("token:"+str(userid)) == token:
                    user = User.query.get(userid)
                    if request.method == "POST" and user.is_blocked:
                        return jsonError(GlobalError.OPERATION_BLOCKED_BY_ADMIN), 403
                    kwargs['current_user'] = user
                    return func(*args, **kwargs)
                else:
                    return jsonError(GlobalError.TOKEN_VALIFY_FAILED), 401
            else:
                return jsonError(GlobalError.TOKEN_VALIFY_FAILED), 401
        except Exception, e:
            db.session.rollback()
            err = GlobalError.UNDEFINED_ERROR
            err['msg'] = str(e)
            return jsonError(err), 403
    return _wrapped

def token_required_unnecessary(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        # 将ImmutableMultiDict变成Dict类型
        request.args = request.args.to_dict()
        # 如果值为空字符串 删掉对应的键 否则后面的request.args.get()会出问题
        for k, v in request.args.items():
            if v == '':
                request.args.pop(k)
        token = request.args.get('token', None) or request.form.get('token', None)
        if not token and request.json:
            token = request.json.get('token', None)
        try:
            if not token:
                kwargs['current_user'] = None
                return func(*args, **kwargs)
            if len(token.split('$')) == 4:
                userid = token.split('$')[1]
                if redisClient.get("token:"+str(userid)) == token:
                    user = User.query.get(userid)
                    kwargs['current_user'] = user
                    return func(*args, **kwargs)
                else:
                    return jsonError(GlobalError.TOKEN_VALIFY_FAILED), 401
            else:
                return jsonError(GlobalError.TOKEN_VALIFY_FAILED), 401
        except Exception,e:
            db.session.rollback()
            err = GlobalError.UNDEFINED_ERROR
            err['msg'] = str(e)
            return jsonError(err), 403
    return _wrapped