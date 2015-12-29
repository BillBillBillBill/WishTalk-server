# -*- coding: utf-8 -*-

from util.token import token_required
from server import db
from api import api, GlobalError, ERROR_REPORT
from model.secret import Secret, SecretReport
from model.onePicture import OnePicture, OnePictureReport
from model.schoolNews import SchoolNews, SchoolNewsReport
from model.association import AssociationPost, AssociationPostReport
from model.internship import Internship, InternshipReport
from model.store import Store, StoreReport
from model.freshmanGuide import FreshmanGuide, FreshmanGuideReport
from model.diskSharing import DiskSharing, DiskSharingReport
from flask import abort, request
from sqlalchemy.exc import IntegrityError
from util.jsonResponse import jsonSuccess, jsonError

'''
重要提示：Model的设计中，需要确保每个Report的类的backref的名称为reports!
每完成一个Report Model，需要往下方的字典添加响应类名
'''

ALLOW_RESOURCE = {  
    'secret': [Secret, SecretReport],
    'one_pic': [OnePicture, OnePictureReport],
    'schoolnews': [SchoolNews, SchoolNewsReport],
    'association': [AssociationPost, AssociationPostReport],
    'internship': [Internship, InternshipReport],
    'store': [Store, StoreReport],
    'freshman_guide': [FreshmanGuide, FreshmanGuideReport],
    'disk_sharing': [DiskSharing, DiskSharingReport]
}

class ReportError:
    EMPTY_CONTENT = {   
        'err': ERROR_REPORT + 1,
        'msg': 'Empty Content'
    }
    INVALID_ID = {   
        'err': ERROR_REPORT + 2,
        'msg': 'Invalid ID'
    }


@api.route('/<string:resource_name>/report/<int:target_id>', methods=['POST'])
@token_required
def report(current_user, resource_name=None, target_id=None):
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    content = request.json.get('content', '')

    if not content:
        return jsonError(ReportError.EMPTY_CONTENT), 403

    try:
        report = Cls[1](current_user.id, target_id, content)
        db.session.add(report)
        db.session.commit()
        return jsonSuccess(), 201
    except IntegrityError, e:
        db.session.rollback()
        return jsonError(ReportError.INVALID_ID), 403


