# -*- coding: utf-8 -*-

from util.token import token_required, token_required_unnecessary
from server import db
from api import api, GlobalError, ERROR_COMMENT
from model.wish import Wish, WishComment
from flask import abort, request
from sqlalchemy.exc import IntegrityError
from util.jsonResponse import jsonSuccess, jsonError
'''
重要提示：Model的设计中，需要确保每个Comment的类的backref的名称为comments!
每完成一个Comment Model，需要往下方的字典添加响应类名
'''

ALLOW_RESOURCE = {  
    'wish': [Wish, WishComment]
}

class CommentError:
    EMPTY_CONTENT = {   
        'err': ERROR_COMMENT + 1,
        'msg': 'Empty Content'
    }
    INVALID_ID = {   
        'err': ERROR_COMMENT + 2,
        'msg': 'Invalid ID'
    }


@api.route('/<string:resource_name>/comment/<int:target_id>', methods=['GET'])
@token_required_unnecessary
def get_comment(current_user, resource_name=None, target_id=None):
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    if not Cls[0].query.get(target_id):
        return jsonError(CommentError.INVALID_ID), 403
    #print target_id, Cls[0].query.get(target_id), Cls[0].query.get(target_id).comments
    comments = Cls[0].query.get(target_id).comments.order_by(Cls[1].create_time.desc()).all()
    limit = int(request.args.get('limit', len(comments)))
    offset = int(request.args.get('offset', 0))
    comments = comments[offset:limit+offset]
    ret = []
    for comment in comments:
        cd = comment.to_dict()
        ret.append(cd)
    #print ret
    return jsonSuccess(ret), 200


@api.route('/<string:resource_name>/comment/<int:target_id>', methods=['POST'])
@token_required
def comment(current_user, resource_name=None, target_id=None):
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    content = request.json.get('content', '')

    if not content:
        return jsonError(CommentError.EMPTY_CONTENT), 403

    try:
        comment = Cls[1](current_user.id, target_id, content)
        db.session.add(comment)
        db.session.commit()
        return jsonSuccess({'insert_id': comment.id}), 201
    except Exception, e:
        db.session.rollback()
        return jsonError(CommentError.INVALID_ID), 403


@api.route('/<string:resource_name>/comment/<int:target_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, resource_name=None, target_id=None):
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    try:
        effect_row = Cls[1].query.filter_by(id=target_id, user_id=current_user.id).delete()
        db.session.commit()
        if effect_row > 0:
            return jsonSuccess(), 200
        else:
            return jsonError(GlobalError.PERMISSION_DENIED), 403
    except Exception, e:
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR)
