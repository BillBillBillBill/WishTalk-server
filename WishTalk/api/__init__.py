# -*- coding: utf-8 -*-

from flask import Blueprint
from util.jsonResponse import jsonSuccess, jsonError

api = Blueprint('api', __name__)

# Define error code
ERROR_GLOBAL        = 0000
ERROR_USER          = 1000
ERROR_SECRET        = 2000
ERROR_ONE_PICTURE   = 3000
ERROR_LIKE          = 4000
ERROR_COMMENT       = 5000
ERROR_REPORT        = 6000
ERROR_COLLECT       = 7000


class GlobalError():
    INVALID_ARGUMENTS = {
        'err': ERROR_GLOBAL + 1, 
        'msg': 'Invalid Arguments'
    }
    TOKEN_VALIFY_FAILED = { 
        'err': ERROR_GLOBAL + 2,
        'msg': 'Token Valify Failed'
    }
    UNDEFINED_ERROR = { 
        'err': ERROR_GLOBAL + 3,
        'msg': ''
    }
    PERMISSION_DENIED = {   
        'err': ERROR_GLOBAL + 4,
        'msg': 'Permission Denied'
    }
    INVALID_FILE = {
        'err': ERROR_GLOBAL + 5,
        'msg': 'Invalid File'
    }
    OPERATION_BLOCKED_BY_ADMIN = {
        'err': ERROR_GLOBAL + 6,
        'msg': 'Operation Blocked By Admin'
    }


#test
@api.route('/', methods=["GET"])
def index():
    from flask import render_template
    return render_template('testapi.html')

#test
@api.route('/sb', methods=["GET"])
def wrong():
    return jsonError(GlobalError.INVALID_ARGUMENTS)

# api's
import user
import secret
import like
import comment
import report
import collect
import image