# -*- coding: utf-8 -*-

from util.token import token_required
from server import db
from api import api, GlobalError, ERROR_COLLECT
from model.secret import Secret, SecretCollect
from model.schoolNews import SchoolNews, SchoolNewsCollect
from model.association import AssociationPost, AssociationPostCollect
from model.internship import Internship, InternshipCollect
from model.store import Store, StoreCollect
from model.product import Product, ProductCollect
from model.freshmanGuide import FreshmanGuide, FreshmanGuideCollect
from model.diskSharing import DiskSharing, DiskSharingCollect
from flask import abort, request
from sqlalchemy.exc import IntegrityError
from util.jsonResponse import jsonSuccess, jsonError

'''
重要提示：Model的设计中，需要确保每个Collect的类的backref的名称为collections!
每完成一个Collect Model，需要往下方的字典添加响应类名
'''

ALLOW_RESOURCE = {  
    'secret': [Secret, SecretCollect],
    'schoolnews': [SchoolNews, SchoolNewsCollect],
    'association': [AssociationPost, AssociationPostCollect],
    'internship': [Internship, InternshipCollect],
    'store': [Store, StoreCollect],
    'product': [Product, ProductCollect],
    'freshman_guide': [FreshmanGuide, FreshmanGuideCollect],
    'disk_sharing': [DiskSharing, DiskSharingCollect]
}

class CollectError:
    UNKNOW = {
        'err': ERROR_COLLECT,
        'msg': 'Unknow Error'
    }
    HAS_COLLECTED = {   
        'err': ERROR_COLLECT + 1,
        'msg': 'Has Collected'
    }
    NOT_COLLECTED = {   
        'err': ERROR_COLLECT + 2,
        'msg': 'Not Collected'
    }


@api.route('/<string:resource_name>/collect', methods=['GET'])
@token_required
def get_collect_secret(current_user, resource_name=None):
    '''
    curl -i -H "Content-Type: application/json" -X GET -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\"}" http://localhost:5000/api/secret/collect
    可选参数:
    limit <int> - 返回记录的数量
    offset <int> - 返回记录的开始位置
    '''
    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)
    collections = Cls[1].query.filter(Cls[1].user_id == current_user.id).all()
    # collections = Cls[0].query.filter(Cls[0].collections.user_id == current_user.id).order_by(Cls[1].create_time.desc()).all()
    limit = int(request.args.get('limit', len(collections)))
    offset = int(request.args.get('offset', 0))
    collections = collections[offset:limit+offset]
    ret = map(lambda cs: cs.to_dict(), collections)
    return jsonSuccess(ret), 200



@api.route('/<string:resource_name>/collect/<int:target_id>', methods=['POST'])
@token_required
def collect(current_user, resource_name=None, target_id=None):
    '''
    curl -i -H "Content-Type: application/json" -X POST -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\"}" "http://localhost:5000/api/secret/collect/6"
    '''
    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    try:
        collect = Cls[1](current_user.id, target_id)
        db.session.add(collect)
        db.session.commit()
        return jsonSuccess(), 201
    except IntegrityError, e:
        db.session.rollback()
        return jsonError(CollectError.HAS_COLLECTED), 403

@api.route('/<string:resource_name>/collect/<int:target_id>', methods=['DELETE'])
@token_required
def cancel_collect(current_user, resource_name=None, target_id=None):
    '''
    curl -i -H "Content-Type: application/json" -X DELETE -d "{\"token\":\"20151005121832$11$18d65889$b4191f2f9076c402e986e5e2463fd7ef7853e325420fe9cda9a42e2cfed2c31e\"}" "http://localhost:5000/api/secret/collect/4"
    '''

    if not target_id:
        return jsonError(GlobalError.INVALID_ARGUMENTS), 403

    Cls = ALLOW_RESOURCE.get(resource_name, None)
    if not Cls:
        abort(404)

    try:
        effect_row = Cls[0].query.get(target_id).collections.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        if effect_row > 0:
            return jsonSuccess(), 200
        else:
            return jsonError(CollectError.NOT_COLLECTED), 403
    except Exception, e:
        db.session.rollback()
        return jsonError(CollectError.UNKNOW), 403

