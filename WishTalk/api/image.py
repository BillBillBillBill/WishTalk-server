# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import uuid
from api import api, GlobalError
from flask import request, Response
from model.image import Image as Image_model
from server import db
from util.jsonResponse import jsonSuccess, jsonError
from config import UPLOAD_PATH
from werkzeug.utils import secure_filename
from PIL import Image
import StringIO

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg', 'PNG', 'JPG', 'JPEG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def get_all_img_list():
    return filter(lambda filename: filename.split('.')[-1] in ALLOWED_EXTENSIONS, os.listdir(UPLOAD_PATH))


@api.route('/image/<string:filename>', methods=['GET'])
def get_image(filename=None):
    if not filename:
        return jsonError(), 404
    else:
        filename = secure_filename(filename)
        if os.path.exists(os.path.join(UPLOAD_PATH, filename)):
            width = int(request.args.get('width', -1))
            height = int(request.args.get('height', -1))
            compress = request.args.get('compress', '')
            format = 'png'
            if compress:
                format = 'jpeg'
            image = Image.open(os.path.join(UPLOAD_PATH, filename))
            w, h = image.size
            if width == -1 and height == -1:
                width = w
                height = h
            elif width == -1 and height != -1:
                width = int(height * 1.0 / h * w)
            elif width != -1 and height == -1:
                height = int(width * 1.0 / w * h)
            image = image.resize((width, height), Image.ANTIALIAS)
            o = StringIO.StringIO()
            image.save(o, format)
            return Response(o.getvalue(), mimetype='image/' + format)
        else:
            return jsonError(), 404

@api.route('/image', methods=['POST'])
def upload_image():
    '''
curl -F "image=@/home/jay/Desktop/1432538993239.jpg" "http://localhost:5000/api/image"
    '''
    try:
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = uuid.uuid4().hex + '.' + image.filename.rsplit('.',1)[1]
            image.save(os.path.join(UPLOAD_PATH, filename))
            image = Image_model(filename)
            db.session.add(image)
            db.session.commit()
            return jsonSuccess({'filename': filename}), 201
        else:
            return jsonError(GlobalError.INVALID_FILE), 403
    except Exception, e:
        print e
        return jsonError(GlobalError.INVALID_FILE), 403


@api.route('/image/<string:filename>', methods=['DELETE'])
def delete_image(filename=None):
    if not filename:
        return jsonError(), 404
    filename = secure_filename(filename)
    try:
        os.remove(os.path.join(UPLOAD_PATH, filename))
        Image_model.query.filter_by(filename=filename).delete()
        db.session.commit()
    except:
        pass
    return jsonSuccess(), 204
