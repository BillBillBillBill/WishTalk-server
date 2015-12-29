# -*- coding: utf-8 -*-

from util.token import token_required, token_required_unnecessary
from server import db
from api import api, ERROR_SECRET, GlobalError
from flask import request
from model.secret import Secret, SecretLike, SecretCollect, SecretComment, SecretReport
from util.jsonResponse import jsonSuccess, jsonError
from sqlalchemy.exc import IntegrityError

'''
api

GET  /secret                        #获取所有爆料，可选参数limit,offset,order_by
GET  /secret/<int:secret_id>        #获取特定id的爆料
POST /secret                        #发表爆料
DELETE  /secret/<int:secret_id>     #删除特定id的爆料

POST /secret/like/<int:secret_id>   #对特定id的爆料点赞
DELETE /secret/like/<int:secret_id> #对特定id取消点赞


GET  /secret/collect                   #获取自己收藏的爆料，可选参数limit,offset，默认收藏时间降序排列
POST /secret/collect/<int:secret_id>   #收藏特定id的爆料
DELETE /secret/collect/<int:secret_id> #取消收藏

GET  /secret/comment/<int:secret_id>   #获取所有该id爆料的评论，可选参数limit,offset，默认时间降序排列
POST /secret/comment/<int:secret_id>   #评论特定id的爆料
DELETE /secret/comment/<int:comment_id> #删除特定id的评论，该评论必须是自己发出的

POST /secret_comment/like/<int:secret_id>   #对特定id的评论点赞
DELETE /secret_comment/like/<int:secret_id> #对特定id评论取消点赞

POST /secret/report/<int:secret_id>    #举报特定id的爆料

'''

class SecretError():
    UnKnown = {
        'err': ERROR_SECRET,
        'msg': 'UnKnown Error'
    }
    SECRET_NOT_EXIST = {    
        'err': ERROR_SECRET + 1,
        'msg': 'Secret not exist'
    }
    EMPTY_TOPIC_OR_CONTENT = {  
        'err': ERROR_SECRET + 2,
        'msg': 'Empty Topic Or Content'
    }
    SECRET_HAS_LIKED = {    
        'err': ERROR_SECRET + 3,
        'msg': 'Secret Has Liked'
    }
    SECRET_HAS_COLLECTED = {    
        'err': ERROR_SECRET + 4,
        'msg': 'Secret Has Collected'
    }


@api.route('/secret', methods=["GET"])
@api.route('/secret/<int:secret_id>', methods=["GET"])
@token_required_unnecessary
def get_secret(current_user, secret_id=None):
    '''
    curl -i -H "Content-Type: application/json" -X GET -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\"}" http://localhost:5000/api/secret
    可选参数:
    limit <int> - 返回记录的数量
    offset <int> - 返回记录的开始位置
    order_by <string> - 排序方式，可选 time或ctr，默认time
    '''
    if secret_id:
        secret = Secret.query.get(secret_id)
        if not secret:
            return jsonError(SecretError.SECRET_NOT_EXIST), 404
        else:
            Secret.query.filter_by(id = secret_id).update({'ctr': secret.ctr + 1})
            db.session.commit()
            ret = secret.to_dict()
            ret['has_like'] = (current_user.like_secrets.filter_by(secret_id = secret_id).count() != 0) if current_user else False
            ret['has_collect'] = (current_user.collect_secrets.filter_by(secret_id = secret_id).count() != 0) if current_user else False
            return jsonSuccess(ret), 200
    else:
        order_by = request.args.get('order_by', 'time')
        if order_by == 'ctr':
            secrets = Secret.query.order_by(Secret.ctr.desc()).all()          #按热度排列
        else:
            secrets = Secret.query.order_by(Secret.create_time.desc()).all()  #按时间排列
        limit = int(request.args.get('limit', len(secrets)))
        offset = int(request.args.get('offset', 0))
        secrets = secrets[offset:limit+offset]
        ret = []
        for secret in secrets:
            s = secret.to_dict()
            s['has_like'] = (current_user.like_secrets.filter_by(secret_id = secret.id).count() != 0) if current_user else False
            s['has_collect'] = (current_user.collect_secrets.filter_by(secret_id = secret.id).count() != 0) if current_user else False
            ret.append(s)
        return jsonSuccess(ret), 200


@api.route('/secret', methods=['POST'])
@token_required
def create_secret(current_user):
    '''
    curl -i -H "Content-Type: application/json" -X POST -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\",\"topic\":\"eat shit\", \"content\":\"eat shit done!!!\"}" "http://localhost:5000/api/secret"

    参数：
    topic <string> - 话题
    cotent <string> - 内容
    
    返回：
    成功 - 新插入的id
    '''
    try:
        topic = request.json.get('topic', '')
        content = request.json.get('content', '')
        print topic, content
        if not topic or not content:
            return jsonError(SecretError.EMPTY_TOPIC_OR_CONTENT), 403
        secret = Secret(current_user.id, topic, content)
        db.session.add(secret)
        db.session.flush()
        insert_id = secret.id
        db.session.commit()
        return jsonSuccess({'insert_id': insert_id}), 201
    except Exception,e:
        db.session.rollback()
        print str(e)
        return jsonError(SecretError.UnKnown), 403

@api.route('/secret/<int:secret_id>', methods=["DELETE"])
@token_required
def delete_secret(current_user, secret_id=None):
    try:
        if not secret_id:
            return jsonError(GlobalError.INVALID_ARGUMENTS), 403
        effect_row = current_user.secrets.filter(Secret.id == secret_id).delete()
        db.session.commit()
        if effect_row > 0:
            return jsonSuccess({'msg': 'Delete secret success'}), 200
        else:
            return jsonError(GlobalError.PERMISSION_DENIED), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR), 403

