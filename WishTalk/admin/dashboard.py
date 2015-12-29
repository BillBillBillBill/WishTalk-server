from model.user import User
from model.store import Store
from model.product import Product
from model.image import Image
from server import db


def get_users_count():
    try:
        return User.query.count()
    except Exception, e:
        print e
        db.session.rollback()
        return 0


def get_store_count():
    try:
        return Store.query.count()
    except Exception, e:
        print e
        db.session.rollback()
        return 0

def get_product_count():
    try:
        return Product.query.count()
    except Exception, e:
        print e
        db.session.rollback()
        return 0

def get_image_count():
    try:
        return Image.query.count()
    except Exception, e:
        print e
        db.session.rollback()
        return 0