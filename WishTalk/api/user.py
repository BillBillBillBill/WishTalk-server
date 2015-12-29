# -*- coding: utf-8 -*-
import random
import time
from hashlib import sha256
from hmac import HMAC

from flask import request

from api import api, ERROR_USER, GlobalError
from model.purse import Purse
from model.user import User, UserInfo
from server import db, redisClient
from util.jsonResponse import jsonSuccess, jsonError
from util.token import token_required
from util.rcim import update_rcim_user

'''
登入/登出对应的服务端资源应该是session，所以相关api应该如下：

GET /session # 获取会话信息 (没实现)
POST /session # 创建新的会话（登入）
PUT /session # 更新会话信息 (没实现)
DELETE /session # 销毁当前会话（登出）

而注册对应的资源是user，api如下：

GET /user/:id # 获取id用户的信息
POST /user # 创建新的用户（注册）
PUT /user # 更新id用户的信息
DELETE /user # 删除id用户（注销） (没实现)
'''

class UserError():
    USER_NOT_EXIST = {
        'err': ERROR_USER + 1,
        'msg': 'User Not Exist'
    }
    PASSWORD_ERROR = {
        'err': ERROR_USER + 2,
        'msg': 'Password Error'
    }
    USERNAME_HAS_EXISTED = {    
        'err': ERROR_USER + 3,
        'msg': 'Username has existed'
    }
    USER_DELETE_FAILED = {
        'err': ERROR_USER + 4,
        'msg': 'User Delete Failed'
    }
    USER_UPDATE_FAILED = {
        'err': ERROR_USER + 5,
        'msg': 'User Update Failed'
    }
    REGISTER_FAILED = { 
        'err': ERROR_USER + 6,
        'msg': 'Register Failed'
    }
    FORM_DATA_INVALID = {   
        'err': ERROR_USER + 7,
        'msg': 'Form Data Invalid'
    }
    CREATE_PURSE_FAIL = {
        'err': ERROR_USER + 8,
        'msg': 'Create Purse Fail'
    }
    MOBILE_NUMBER_ILLEGAL = {
        'err': ERROR_USER + 9,
        'msg': 'Mobile Number Illegal'
    }
    CHECKCODE_ERROR = {
        'err': ERROR_USER + 10,
        'msg': 'Checkcode Error'
    }


def get_enc_password(raw_password, salt=None):
    '''
    密码加密，输入为盐
    若没有输入盐，随机生成盐
    返回值为salt$password
    '''
    if salt is None:
        salt = sha256(str(random.random())).hexdigest()[-8:]
    if isinstance(raw_password, unicode):
        raw_password = raw_password.encode('utf-8')
    # password = sha256('%s%s' % (salt, raw_password)).hexdigest()
    enc_password = '%s$%s' % (salt, HMAC(str(salt), str(raw_password), sha256).hexdigest())
    return enc_password

def check_password(password, enc_password):
    '''
    检验密码是否正确，输入为原始密码与加密后的密码
    返回值为True或False
    '''
    try:
        salt = enc_password.split('$')[0]
        return enc_password == get_enc_password(password, salt)
    except Exception, e:
        return False

def get_user(username=None,id=None):
    '''
    在数据库中通过用户名/ID查询用户
    '''
    user = None
    if username:
        user = User.query.filter_by(username = username).one()
    if id:
        user = User.query.get(id)
    return user

def register(username, password, nickname, avatar):
    '''
    输入为用户名，密码，邮箱
    返回值为token
    '''
    try:
        enc_password = get_enc_password(password)
        # print u"用户：%s" % username
        # print u"原密码：%s" % password
        # print u"密码：%s" % enc_password
        # 存入数据库
        newUser = User(username, enc_password, nickname, avatar)
        db.session.add(newUser)
        db.session.flush()
        user_info = UserInfo(newUser.id)
        db.session.add(user_info)
        db.session.commit()
        # 创建钱包
        try:
            purse = Purse(newUser.id)
            db.session.add(purse)
            db.session.flush()
            db.session.commit()
        except Exception, e:
            print e
            return jsonError(UserError.CREATE_PURSE_FAIL), 400
        return login(username, password)
    except Exception, e:
        db.session.rollback()
        print "用户注册失败" + str(e)
        return False
    finally:
        # 记得关闭！！
        db.session.close()

def login(username, password):
    '''
    token格式为时间戳+uid+加密后的密码
    失败返回值为False
    成功返回值为token
    '''
    try:
        nowTime = time.strftime('%Y%m%d%H%M%S', time.localtime())
        user = get_user(username=username)
        enc_password = user.password
        id = user.id
        # 验证该密码
        assert check_password(password, enc_password) == True
        token = "%s$%s$%s" % (nowTime, id, enc_password)
        print "token:", token
        # 把该token存进redis中 键为id，值为token
        redisClient.set("token:" + str(id), token)
        #print user.username + u"登录成功"
        return {"token": token}
    except Exception, e:
        print "用户登录失败" + str(e)
        return False

def delete_user_by_id(id):
    '''
    :param id: 用户的ID
    :return: True/Flase
    删除用户，目前没有加条件
    '''
    try:
        redisClient.delete("token:" + str(id))
        User.query.filter_by(id = id).delete()
        db.session.commit()
        return True
    except Exception, e:
        db.session.rollback()
        print "删除用户失败" + str(e)
        return False

def update_user(id, username='', password='', nickname='', avatar=''):
    try:
        updateDict = {}
        if password:
            # 更新密码，删除token
            redisClient.delete("token:" + str(id))
            updateDict['password'] = get_enc_password(password)
        if username:
            updateDict['username'] = username
        if nickname:
            updateDict['nickname'] = nickname
        if avatar:
            updateDict['avatar'] = avatar
        if updateDict:
            User.query.filter_by(id = id).update(updateDict)
        db.session.commit()
        return True
    except Exception, e:
        db.session.rollback()
        print u"更新用户信息失败" + str(e)
        return False


@api.route('/user/checkcode', methods=["POST"])
def get_register_checkcode():
    try:
        from util.send_sms import send_sms_checkcode
        import random
        phone = request.json.get('phone', '')
        user = User.query.filter(User.username == phone).first()
        if user:
            return jsonError(UserError.USERNAME_HAS_EXISTED), 403
        code = random.randint(100000, 1000000)  # 六位验证码
        stat = send_sms_checkcode(phone, code)
        if stat:
            redisClient.set("checkcode:" + phone, code)
            return jsonSuccess(), 200
        else:
            return jsonError(UserError.MOBILE_NUMBER_ILLEGAL), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(UserError.CHECKCODE_ERROR), 403

@api.route('/user/forget_checkcode', methods=["POST"])
def get_forget_checkcode():
    try:
        from util.send_sms import send_sms_forget_code
        import random
        phone = request.json.get('phone', '')
        user = User.query.filter(User.username == phone).first()
        if not user:
            return jsonError(UserError.USER_NOT_EXIST), 403
        code = random.randint(100000, 1000000)  # 六位验证码
        stat = send_sms_forget_code(phone, code)
        if stat:
            redisClient.set("forgetcheckcode:" + phone, code)
            return jsonSuccess(), 200
        else:
            return jsonError(UserError.MOBILE_NUMBER_ILLEGAL), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(UserError.CHECKCODE_ERROR), 403

@api.route('/user/password_reset', methods=["POST"])
def reset_password():
    try:
        username = request.json.get('username', '')
        new_password = request.json.get('new_password', '')
        checkcode = request.json.get('checkcode', '')
        if redisClient.get("forgetcheckcode:" + username) != checkcode:
            return jsonError(UserError.CHECKCODE_ERROR)
        enc_password = get_enc_password(new_password)
        User.query.filter_by(username=username).update({"password": enc_password})
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonError(GlobalError.UNDEFINED_ERROR)
        redisClient.delete("forgetcheckcode:" + username)
        return jsonSuccess(), 200
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR)

@api.route('/user', methods=["POST"])
def user_register():
    '''
    注册用户
    curl -i -H "Content-Type: application/json" -X POST -d "{\"username\":\"foo\",\"password\":\"bar\",\"email\":\"foo@bar.com\"}" http://localhost:5000/api/user
    '''
    try:
        if not request.json:
            return jsonError(GlobalError.INVALID_ARGUMENTS), 400
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        nickname = request.json.get('nickname', '')
        avatar = request.json.get('avatar', '')
        if not username and not password:
            return jsonError(UserError.FORM_DATA_INVALID), 400
        user = User.query.filter(User.username == username).first()
        if user:
            return jsonError(UserError.USERNAME_HAS_EXISTED), 403
        if redisClient.get("checkcode:" + username) != password:
            return jsonError(UserError.CHECKCODE_ERROR), 403
        ret = register(username, password, nickname, avatar)
        if ret:
            data = ret
            redisClient.delete("checkcode:" + username)
            return jsonSuccess(data), 201
        else:
            return jsonError(UserError.REGISTER_FAILED), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR), 403

@api.route('/user', methods=["GET"])
@api.route('/user/<int:user_id>', methods=["GET"])
@token_required
def get_user_info(current_user, user_id=None):
    '''
    获取用户信息
    curl -i -H "Content-Type: application/json" -X GET -d "{\"token\":\"\"}" http://localhost:5000/api/user/5
    '''
    try:
        if not user_id:
            return jsonSuccess(current_user.user_info.first().to_dict()), 200
        else:
            user = get_user(id = user_id)
            if user:
                return jsonSuccess(user.user_info.first().to_dict()), 200
            else:
                return jsonError(UserError.USER_NOT_EXIST), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR), 403

"""
@api.route('/user', methods=["DELETE"])
def delete_user():
    '''
    curl -i -H "Content-Type: application/json" -X DELETE -d '{"id":"1"}' http://localhost:5000/api/user
    '''
    if not request.json or not 'id' in request.json:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 400
    id = request.json['id']
    if delete_user_by_id(id):
        return jsonSuccess({'msg':'delete user success'}), 200
    else:
        return jsonError(UserError.USER_DELETE_FAILED), 403
"""

@api.route('/user', methods=["PUT"])
@token_required
def update(current_user):
    '''
    curl -i -H "Content-Type: application/json" -X PUT -d "{\"token\":\"\", \"password\":\"hehe\"}" http://localhost:5000/api/user
    '''
    '''
    :param token: token
    :param password:
    :param email:
    :return: True/Flase
    '''
    try:
        token = request.json['token']

        if request.json.get("nickname") != None:
            User.query.filter_by(id = current_user.id).update({"nickname": request.json.get("nickname", "")})

        if request.json.get("password") != None:
            if request.json['password'] == '':
                return jsonError(UserError.USER_UPDATE_FAILED), 403
            # 更新密码，删除token
            # redisClient.delete(current_user.id)
            salt = token.split('$')[2]
            enc_password = get_enc_password(request.json.get("password", ""), salt)
            User.query.filter_by(id = current_user.id).update({"password": enc_password})

        if request.json.get("avatar") != None:
            User.query.filter_by(id = current_user.id).update({"avatar": request.json.get("avatar", "")})

        userInfo = UserInfo.query.filter_by(user_id = current_user.id)
        userInfo.update(userInfo.first().get_update_dict(request.json))

        db.session.commit()

        if request.json.get("avatar") or request.json.get("nickname"):
            update_rcim_user(current_user)

        return jsonSuccess({'msg':'update user success'}), 200
    except Exception, e:
        print u"更新信息失败", str(e)
        db.session.rollback()
        return jsonError(UserError.USER_UPDATE_FAILED), 403

@api.route('/session', methods=["POST"])
def user_login():
    '''
    curl -i -H "Content-Type: application/json" -X POST -d "{\"username\":\"foo\",\"password\":\"bar\"}" http://localhost:5000/api/session
    '''
    if not request.json:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 400
    ret = login(
        request.json.get('username', ''),
        request.json.get('password', '')
    )
    if ret:
        data = ret
        return jsonSuccess(data), 200
    else:
        return jsonError(UserError.PASSWORD_ERROR), 403

@api.route('/session', methods=["DELETE"])
@token_required
def user_logout(current_user):
    '''
    curl -i -H "Content-Type: application/json" -X DELETE -d "{\"token\":\"\"}" http://localhost:5000/api/session
    '''
    redisClient.delete("token:" + str(current_user.id))
    return jsonSuccess({'msg': 'logout success'})
