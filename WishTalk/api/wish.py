# -*- coding: utf-8 -*-

from util.token import token_required, token_required_unnecessary
from server import db
from api import api, ERROR_WISH, GlobalError
from flask import request
from model.wish import Wish, WishLike, WishComment
from util.jsonResponse import jsonSuccess, jsonError
from datetime import datetime


'''
api

GET  /wish                      #获取所有愿望，可选参数limit,offset,order_by
GET  /wish/<int:wish_id>        #获取特定id的愿望
POST /wish                      #发表愿望
DELETE  /wish/<int:wish_id>     #删除特定id的愿望
PUT  /wish/<int:wish_id>        #对特定id的愿望进行操作 参数为action

POST /wish/like/<int:wish_id>   #对特定id的愿望点赞
DELETE /wish/like/<int:wish_id> #对特定id取消点赞

GET  /wish/comment/<int:wish_id>   #获取所有该id愿望的评论，可选参数limit,offset，默认时间降序排列
POST /wish/comment/<int:wish_id>   #评论特定id的愿望
DELETE /wish/comment/<int:comment_id> #删除特定id的评论，该评论必须是自己发出的

'''

class WishError():
    UnKnown = {
        'err': ERROR_WISH,
        'msg': 'UnKnown Error'
    }
    WISH_NOT_EXIST = {
        'err': ERROR_WISH + 1,
        'msg': 'Wish not exist'
    }
    EMPTY_TOPIC_OR_CONTENT = {  
        'err': ERROR_WISH + 2,
        'msg': 'Empty Topic Or Content'
    }
    WISH_HAS_LIKED = {
        'err': ERROR_WISH + 3,
        'msg': 'Wish Has Liked'
    }
    ACTION_NOT_ALLOW = {
        'err': ERROR_WISH + 4,
        'msg': 'Action Not Allow'
    }
    WISH_STATUS_WRONG = {
        'err': ERROR_WISH + 5,
        'msg': 'Wish Status Wrong'
    }
    SELF_TAKING_ERROR = {
        'err': ERROR_WISH + 6,
        'msg': 'Self Taking Error'
    }


@api.route('/wish', methods=["GET"])
@api.route('/wish/<int:wish_id>', methods=["GET"])
@token_required_unnecessary
def get_wish(current_user, wish_id=None):
    '''
    curl -i -H "Content-Type: application/json" -X GET -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\"}" http://localhost:5000/api/wish
    可选参数:
    limit <int> - 返回记录的数量
    offset <int> - 返回记录的开始位置
    order_by <string> - 排序方式，可选 time或ctr，默认time
    '''
    if wish_id:
        wish = Wish.query.get(wish_id)
        if not wish:
            return jsonError(WishError.WISH_NOT_EXIST), 404
        else:
            Wish.query.filter_by(id = wish_id).update({'ctr': wish.ctr + 1})
            db.session.commit()
            ret = wish.to_dict()
            ret['has_like'] = (current_user.like_wishs.filter_by(wish_id = wish_id).count() != 0) if current_user else False
            return jsonSuccess(ret), 200
    else:
        order_by = request.args.get('order_by', 'time')
        if order_by == 'ctr':
            wishs = Wish.query.order_by(Wish.ctr.desc()).all()          #按热度排列
        else:
            wishs = Wish.query.order_by(Wish.create_time.desc()).all()  #按时间排列
        limit = int(request.args.get('limit', len(wishs)))
        offset = int(request.args.get('offset', 0))
        wishs = wishs[offset:limit+offset]
        ret = []
        for wish in wishs:
            s = wish.to_dict()
            s['has_like'] = (current_user.like_wishs.filter_by(wish_id = wish.id).count() != 0) if current_user else False
            ret.append(s)
        return jsonSuccess(ret), 200


@api.route('/my_wish', methods=["GET"])
@token_required
def get_my_wish(current_user):
    '''
    可选参数:
    limit <int> - 返回记录的数量
    offset <int> - 返回记录的开始位置
    order_by <string> - 排序方式，可选 time或ctr，默认time
    '''
    order_by = request.args.get('order_by', 'time')
    if order_by == 'ctr':
        wishs = current_user.self_wishes.order_by(Wish.ctr.desc()).all()          #按热度排列
    else:
        wishs = current_user.self_wishes.order_by(Wish.create_time.desc()).all()  #按时间排列
    limit = int(request.args.get('limit', len(wishs)))
    offset = int(request.args.get('offset', 0))
    wishs = wishs[offset:limit+offset]
    ret = []
    for wish in wishs:
        s = wish.to_dict()
        s['has_like'] = (current_user.like_wishs.filter_by(wish_id = wish.id).count() != 0) if current_user else False
        ret.append(s)
    return jsonSuccess(ret), 200

@api.route('/my_help_wish', methods=["GET"])
@token_required
def get_my_help_wish(current_user):
    '''
    可选参数:
    limit <int> - 返回记录的数量
    offset <int> - 返回记录的开始位置
    order_by <string> - 排序方式，可选 time或ctr，默认time
    '''
    order_by = request.args.get('order_by', 'time')
    if order_by == 'ctr':
        wishs = current_user.help_wishes.order_by(Wish.ctr.desc()).all()          #按热度排列
    else:
        wishs = current_user.help_wishes.order_by(Wish.create_time.desc()).all()  #按时间排列
    limit = int(request.args.get('limit', len(wishs)))
    offset = int(request.args.get('offset', 0))
    wishs = wishs[offset:limit+offset]
    ret = []
    for wish in wishs:
        s = wish.to_dict()
        s['has_like'] = (current_user.like_wishs.filter_by(wish_id = wish.id).count() != 0) if current_user else False
        ret.append(s)
    return jsonSuccess(ret), 200

@api.route('/wish', methods=['POST'])
@token_required
def create_wish(current_user):
    '''
    curl -i -H "Content-Type: application/json" -X POST -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\",\"topic\":\"eat shit\", \"content\":\"eat shit done!!!\"}" "http://localhost:5000/api/wish"

    参数：
    title <string> - 话题
    cotent <string> - 内容
    
    返回：
    成功 - 新插入的id
    '''
    try:
        title = request.json.get('title', '')
        location = request.json.get('location', '')
        content = request.json.get('content', '')
        out_time = request.json.get('out_time', '')
        print title, content
        if not title or not content:
            return jsonError(WishError.EMPTY_TOPIC_OR_CONTENT), 403
        wish = Wish(current_user.id, title, content, out_time, location)
        db.session.add(wish)
        db.session.flush()
        insert_id = wish.id
        db.session.commit()
        return jsonSuccess({'insert_id': insert_id}), 201
    except Exception,e:
        db.session.rollback()
        print str(e)
        return jsonError(WishError.UnKnown), 403



@api.route('/wish/<int:wish_id>', methods=["PUT"])
@token_required
def action_on_wish(current_user, wish_id=None):
    try:
        if not wish_id:
            return jsonError(GlobalError.INVALID_ARGUMENTS), 403

        allow_actions = ["take", "giveup", "finish", "close"]
        action = request.json.get("action", "")

        if action not in allow_actions:
            return jsonError(WishError.ACTION_NOT_ALLOW), 403

        wish = Wish.query.get(wish_id)
        if not wish:
            return jsonError(WishError.WISH_NOT_EXIST), 404

        if action == "take" or action == "giveup":
            if wish.owner_id == current_user.id:
                return jsonError(GlobalError.PERMISSION_DENIED), 403

            if action == "take":
                if wish.status != "unfinished":
                    return jsonError(WishError.WISH_STATUS_WRONG), 403
                else:
                    wish.status = "finishing"
                    wish.helper_id = current_user.id
                    db.session.commit()
                    return jsonSuccess({'msg': 'Take wish success'}), 200

            if action == "giveup":
                if wish.helper_id != current_user.id:
                    return jsonError(GlobalError.PERMISSION_DENIED), 403
                if wish.status != "finishing":
                    return jsonError(WishError.WISH_STATUS_WRONG), 403
                else:
                    wish.status = "unfinished"
                    wish.helper_id = None
                    db.session.commit()
                    return jsonSuccess({'msg': 'Giveup wish success'}), 200

        if action == "finish" or action == "close":
            if wish.owner_id != current_user.id:
                return jsonError(GlobalError.PERMISSION_DENIED), 403

            if action == "finish":
                # 在任何情况下都可以把状态变成完成 即使没有人帮助
                # if wish.status != "finishing":
                #     return jsonError(WishError.WISH_STATUS_WRONG), 403
                # else:
                wish.status = "finished"
                wish.finished_time = datetime.now()
                db.session.commit()
                return jsonSuccess({'msg': 'Finish wish success'}), 200

            if action == "close":
                # wish.status = "closed"
                # wish.helper_id = None
                wish.delete()
                db.session.commit()
                return jsonSuccess({'msg': 'Close wish success'}), 200
        return jsonError(WishError.WISH_STATUS_WRONG), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR), 403

@api.route('/wish/<int:wish_id>', methods=["DELETE"])
@token_required
def delete_wish(current_user, wish_id=None):
    try:
        if not wish_id:
            return jsonError(GlobalError.INVALID_ARGUMENTS), 403
        effect_row = current_user.wishs.filter(Wish.id == wish_id).delete()
        db.session.commit()
        if effect_row > 0:
            return jsonSuccess({'msg': 'Delete wish success'}), 200
        else:
            return jsonError(GlobalError.PERMISSION_DENIED), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR), 403

