# -*- coding: utf-8 -*-
#!/usr/bin/env python

from util.token import token_required
from util.rcim import client
from util.jsonResponse import jsonSuccess, jsonError
from api import api, GlobalError
from config import HOSTNAME
from server import redisClient



@api.route("/rcim/token", methods=["GET"])
@token_required
def get_rcim_token(current_user):
    redis_key = "rcimtoken:" + str(current_user.id)
    rcim_token = redisClient.get(redis_key)
    if rcim_token:
        return jsonSuccess({"rcim_token": rcim_token}), 200
    avatar_full_path = "http://" +\
                       HOSTNAME +\
                       "/api/image/" +\
                       current_user.avatar
    result = client.user_get_token(
            current_user.id, # 用户id
            current_user.nickname, # 用户昵称
            avatar_full_path) # 用户头像路径
    if result['code'] == 200:
        rcim_token = result['token']
        redisClient.set(redis_key, rcim_token)
        return jsonSuccess({"rcim_token": rcim_token}), 200
    else:
        return jsonError(GlobalError.UNDEFINED_ERROR), 403




