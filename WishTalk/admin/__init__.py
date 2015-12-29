# -*- coding: utf-8 -*-
from flask import render_template
from flask import Blueprint
from flask import request
from server import db
from dashboard import get_users_count, get_image_count
from model import *
import json
import inspect


admin = Blueprint('admin', __name__)


ALLOW_TABLE_LIST = []

ALLOW_TABLE_LIST_OTHER = []
ALLOW_TABLE_LIST_COMMENT = []

ALLOW_TABLE_MAP = {}

# 重新载入名称
def load_ALLOW_TABLE_LIST():
    global real_name_to_display_name_dict
    global ALLOW_TABLE_LIST_OTHER
    global ALLOW_TABLE_LIST_COMMENT
    global ALLOW_TABLE_MAP
    global ALLOW_TABLE_LIST

    ALLOW_TABLE_LIST_OTHER = []
    ALLOW_TABLE_LIST_COMMENT = []

    # 让其有序 用列表存keys
    ALLOW_TABLE_LIST = [
        ['wish', u'心愿'],
        ['user', u'用户'],
        ['user_info', u'用户详细信息'],
        ['upload_image', u'上传的照片'],
        ['comment_wish', u'心愿评论'],
    ]
    for table in ALLOW_TABLE_LIST:
        ALLOW_TABLE_LIST_OTHER.append(table)

    ALLOW_TABLE_MAP = {
        'others': ALLOW_TABLE_LIST_OTHER,
        'comments': ALLOW_TABLE_LIST_COMMENT,
    }

load_ALLOW_TABLE_LIST()

TABLE_NAME_TO_MODEL = {
    'wish': wish.Wish,
    'user': user.User,
    'user_info': user.UserInfo,
    'upload_image': image.Image,
    'comment_wish': wish.WishComment,
}

# 创建新项需要的键
TABLE_NAME_TO_KEYS = dict()
for name, model in TABLE_NAME_TO_MODEL.items():
    TABLE_NAME_TO_KEYS[name] = inspect.getargspec(model.__init__)

TABLE_NAME_TO_DISPLAY_NAME = dict()
for x, y in ALLOW_TABLE_LIST:
    TABLE_NAME_TO_DISPLAY_NAME[x] = y


@admin.route('/', methods=["GET"])
def render_index():
    return render_template(
        'index.html',
        title=u'心愿说APP-仪表盘',
        module_name=u'仪表盘',
        tables_name=ALLOW_TABLE_MAP,
        users_count=get_users_count(),
        image_count=get_image_count()
    )


@admin.route('/widgets', methods=["GET"])
def render_widgets():
    return render_template(
        'widgets.html',
        tables_name=ALLOW_TABLE_MAP,
        title=u'心愿说APP-插件',
        module_name=u'插件'
    )


@admin.route('/charts', methods=["GET"])
def render_charts():
    return render_template(
        'charts.html',
        tables_name=ALLOW_TABLE_MAP,
        title=u'心愿说APP-图表',
        module_name=u'图表'
    )


@admin.route('/tables/<string:table_name>', methods=["GET"])
def render_tables(table_name=None):
    table_new_data_keys = {}
    for k in TABLE_NAME_TO_KEYS:
        table_new_data_keys[k] = TABLE_NAME_TO_KEYS[k][0][1:]

    # 插入数据所需的键（部分，用于构造）
    table_new_data_keys = table_new_data_keys.get(table_name)

    # 获取数据
    table_source = [i.to_dict() for i in TABLE_NAME_TO_MODEL[table_name].query.all()]
    # 转换成字符串(用于渲染数据)
    table_data_str = json.dumps(table_source)
    # 数据的键(全部，用于表头)
    table_data_keys = table_source[0].keys() if table_source else None

    # 用于控制按钮是否可见
    btn_control = {}
    enable_update_btn_table_list = [
        'wish',
        'user',
        'user_info',
    ]
    enable_delete_btn_table_list = [
        'wish',
        'user',
        'user_info',
        'upload_image',
        'comment_wish',
    ]
    enable_create_btn_table_list = [
        'wish',
        'user',
        'comment_wish',
    ]
    enable_show_img_btn_table_list = [
        'upload_image',
    ]

    btn_control['update_btn'] = True if table_name in enable_update_btn_table_list else False
    btn_control['delete_btn'] = True if table_name in enable_delete_btn_table_list else False
    btn_control['create_btn'] = True if table_name in enable_create_btn_table_list else False
    btn_control['show_img_btn'] = True if table_name in enable_show_img_btn_table_list else False

    if table_name in TABLE_NAME_TO_DISPLAY_NAME.keys():
        return render_template(
            'tables.html',
            btn_control=btn_control,
            tables_name=ALLOW_TABLE_MAP,
            table_data_keys=table_data_keys,
            table_data_str=table_data_str,
            table_new_data_keys=table_new_data_keys,
            title=u'心愿说APP-' + TABLE_NAME_TO_DISPLAY_NAME[table_name] + u'表格',
            module_name=TABLE_NAME_TO_DISPLAY_NAME[table_name]
        )


@admin.route('/img_file_manage', methods=["GET"])
def render_forms():
    return render_template(
        'img_file_manage.html',
        tables_name=ALLOW_TABLE_MAP,
        title=u'心愿说APP-图片上传',
        module_name=u'图片上传'
    )


@admin.route('/panels', methods=["GET"])
def render_panels():
    return render_template(
        'panels.html',
        tables_name=ALLOW_TABLE_MAP,
        title=u'心愿说APP-面板',
        module_name=u'面板'
    )


@admin.route('/login', methods=["GET"])
def render_login():
    return render_template('login.html')


# 创建
@admin.route('/tables/<string:table_name>', methods=["POST"])
def create_table_row(table_name):
    try:
        j = request.json
        table_model = TABLE_NAME_TO_MODEL[table_name]
        keys = TABLE_NAME_TO_KEYS[table_name][0][1:]
        # 增加用户的情况
        if table_name == 'user':
            from api.user import register, login
            if register(j.get("username"), j.get("password"), j.get("nickname"), j.get("avatar")):
                return "", 200
            else:
                return "", 400
        new_row = table_model(*[j.get(k) for k in keys])
        db.session.add(new_row)
        db.session.commit()
        return "", 200
    except Exception, e:
        db.session.rollback()
        print e
        return "", 400


# 更新
@admin.route('/tables/<string:table_name>/<int:model_id>', methods=["PUT"])
def update_table_row(table_name, model_id):
    try:
        j = request.json
        table_model = TABLE_NAME_TO_MODEL[table_name]
        keys = TABLE_NAME_TO_KEYS[table_name][0][1:]
        # 修改用户的情况
        if table_name == 'user':
            from api.user import update_user
            if update_user(model_id, j.get("username"), j.get("password"), j.get("nickname"), j.get("avatar")):
                return "", 200
            else:
                return "", 400
        updateDict = {}
        for k, v in j.items():
            if k in dir(table_model):
                try:
                    if k in ['visible', 'is_blocked']:
                        if v in ['true', '1', 'True']:
                            updateDict[k] = True
                        else:
                            updateDict[k] = False
                        continue
                    if isinstance(json.loads(v), dict):
                        continue
                    updateDict[k] = v
                except Exception, e:
                    print e
                    updateDict[k] = v

        table_model.query.filter_by(id = model_id).update(updateDict)
        db.session.commit()
        return "", 200
    except Exception, e:
        db.session.rollback()
        print e
        return "", 400


# 删除
@admin.route('/tables/<string:table_name>/<int:model_id>', methods=["DELETE"])
def delete_table_row(table_name, model_id):
    try:
        table_model = TABLE_NAME_TO_MODEL[table_name]
        table_model.query.filter(table_model.id==model_id).delete()
        db.session.commit()
        return "", 200
    except Exception, e:
        db.session.rollback()
        print e
        return "", 400
