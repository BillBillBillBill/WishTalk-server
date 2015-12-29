# -*- coding: utf-8 -*-

from util.message import push_message
from util.token import token_required
from server import db
from api import api, GlobalError, ERROR_LIKE
from model.secret import Secret, SecretLike, SecretComment, SecretCommentLike
from model.onePicture import OnePicture, OnePictureLike
from model.schoolNews import SchoolNews, SchoolNewsLike, SchoolNewsComment, SchoolNewsCommentLike
from model.association import AssociationPost, AssociationPostLike, AssociationPostComment, AssociationPostCommentLike
from model.internship import Internship, InternshipLike, InternshipComment, InternshipCommentLike
from model.freshmanGuide import FreshmanGuide, FreshmanGuideLike, FreshmanGuideComment, FreshmanGuideCommentLike
from model.diskSharing import DiskSharing, DiskSharingLike, DiskSharingComment, DiskSharingCommentLike
from flask import abort
from sqlalchemy.exc import IntegrityError
from util.jsonResponse import jsonSuccess, jsonError

'''
重要提示：Model的设计中，需要确保每个Like的类的backref的名称为likers!
每完成一个Like Model，需要往下方的字典添加响应类名
'''

ALLOW_RESOURCE = {  
    'secret': [Secret, SecretLike],
    'secret_comment': [SecretComment, SecretCommentLike],
    'one_pic': [OnePicture, OnePictureLike],
    'schoolnews': [SchoolNews, SchoolNewsLike],
    'schoolnews_comment': [SchoolNewsComment, SchoolNewsCommentLike],
    'association': [AssociationPost, AssociationPostLike],
    'association_comment': [AssociationPostComment, AssociationPostCommentLike],
    'internship': [Internship, InternshipLike],
    'internship_comment': [InternshipComment, InternshipCommentLike],
    'freshman_guide': [FreshmanGuide, FreshmanGuideLike],
    'freshman_guide_comment': [FreshmanGuideComment, FreshmanGuideCommentLike],
    'disk_sharing': [DiskSharing, DiskSharingLike],
    'disk_sharing_comment': [DiskSharingComment, DiskSharingCommentLike]
}

class LikeError:
    HAS_LIKED = {   
        'err': ERROR_LIKE + 1,
        'msg': 'Has Liked'
    }
    NOT_LIKED = {   
        'err': ERROR_LIKE + 2,
        'msg': 'Not Liked'
    }

@api.route('/<string:resource_name>/like/<int:target_id>', methods=['POST'])
@token_required
def like(current_user, resource_name=None, target_id=None):
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    try:
        like = Cls[1](current_user.id, target_id)
        db.session.add(like)
        db.session.commit()
        target = Cls[0].query.get(target_id)
        if target.user_id != current_user.id:
            push_message(resource_name + '_like', target, current_user)
        return jsonSuccess(), 201
    except IntegrityError, e:
        db.session.rollback()
        return jsonError(LikeError.HAS_LIKED), 403

@api.route('/<string:resource_name>/like/<int:target_id>', methods=['DELETE'])
@token_required
def cancel_like(current_user, resource_name=None, target_id=None):
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)
    try:
        effect_row = Cls[0].query.get(target_id).likers.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        if effect_row > 0:
            return jsonSuccess(), 200
        else:
            return jsonError(LikeError.NOT_LIKED), 403
    except Exception, e:
        print e
        db.session.rollback()
        return jsonError(GlobalError.UNDEFINED_ERROR), 403
