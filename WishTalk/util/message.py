# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import uuid
from datetime import datetime
from server import redisClient

MESSAGE_PREFIX = "message:"

def push_message(message_type, target, origin_user, content=''):
    '''
    增加新消息
    :param message_type: 消息类型
    :param target: 目标内容
    :param origin_user: 用户来源
    :return:
    '''
    try:
        target_user_id = target.user_id
        message_list_str = redisClient.get(MESSAGE_PREFIX + str(target_user_id)) or "[]"
        message_list = json.loads(message_list_str)
        msg = {
            "type": message_type,
            "target": target.to_dict(),
            "user": origin_user.to_dict(),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": content,
            "unread": True,
            "id": uuid.uuid4().hex
        }
        message_list.append(msg)
        message_list_str = json.dumps(message_list)
        redisClient.set(MESSAGE_PREFIX + str(target_user_id), message_list_str)
    except Exception, e:
        print e

def get_message(current_user_id):
    try:
        message_list_str = redisClient.get(MESSAGE_PREFIX + str(current_user_id)) or "[]"
        message_list = json.loads(message_list_str)
        message_list.reverse()
        return message_list
    except Exception, e:
        print e

def delete_message(current_user_id, message_id):
    message_list_str = redisClient.get(MESSAGE_PREFIX + str(current_user_id)) or "[]"
    message_list = json.loads(message_list_str)
    for message in message_list:
        if message.get("id") == message_id:
            message_list.remove(message)
            break
    message_list_str = json.dumps(message_list)
    redisClient.set(MESSAGE_PREFIX + str(current_user_id), message_list_str)

def set_read_message(current_user_id, message_id):
    message_list_str = redisClient.get(MESSAGE_PREFIX + str(current_user_id)) or "[]"
    message_list = json.loads(message_list_str)
    for message in message_list:
        if message.get("id") == message_id:
            message['unread'] = False
            break
    message_list_str = json.dumps(message_list)
    redisClient.set(MESSAGE_PREFIX + str(current_user_id), message_list_str)