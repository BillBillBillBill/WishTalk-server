# -*- coding: utf-8 -*-
#!/usr/bin/env python

from util.rong import ApiClient
from config import RC_APPKEY, RC_APPSECRET, HOSTNAME
import os

os.environ.setdefault('rongcloud_app_key', RC_APPKEY)
os.environ.setdefault('rongcloud_app_secret', RC_APPSECRET)
client = ApiClient()

def update_rcim_user(current_user):
    """
    更新用户信息，用户更新昵称或头像时触发
    :param current_user:
    :return:
    """
    avatar_full_path = "http://" +\
                       HOSTNAME +\
                       "/api/image/" +\
                       current_user.avatar
    result = client.user_refresh(
            current_user.id,
            current_user.nickname,
            avatar_full_path)
    if result['code'] == 200:
        return True
    else:
        return False

def rcim_block_user(user_id, interval):
    """
    管理员方法，封禁用户
    :param user_id: 用户id
    :param interval: 封禁时长，单位为分钟
    :return:
    """
    result = client.user_block(str(user_id), int(interval))
    if result['code'] == 200:
        return True
    else:
        return False

def rcim_unblock_user(user_id):
    """
    管理员方法，解除封禁
    :param user_id: 用户id
    :return:
    """
    result = client.user_unblock(str(user_id))
    if result['code'] == 200:
        return True
    else:
        return False

def rcim_get_block_list():
    """
    获取封禁用户列表
    :return: 格式[{"userId":"jlk456j5","blockEndTime":"2015-01-11 01:28:20"}]
    """
    result = client.user_block_query()
    if result['code'] == 200:
        return result['users']
    else:
        return []
