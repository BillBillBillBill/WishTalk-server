# -*- coding: utf-8 -*-

from flask import jsonify


def jsonSuccess(data=None):
    """
参数：
    `data`(dict) 数据
返回格式：(string)
    "{stat:1,data:{a:1,b:2}}"
    """
    return jsonify(stat=1, data=data)

def jsonError(msg={}):
    """
参数：
    `msg`(dict) 错误信息
返回格式：(string)
    "{stat:0,err:x,msg:balabala}"
    """
    return jsonify(stat=0, **msg)