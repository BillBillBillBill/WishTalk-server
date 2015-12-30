from model.user import User
from model.image import Image
from model.wish import Wish, WishComment
from server import db


def get_users_count():
    try:
        return User.query.count()
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


def get_wish_count():
    try:
        return Wish.query.count()
    except Exception, e:
        print e
        db.session.rollback()
        return 0


def get_wish_comment_count():
    try:
        return WishComment.query.count()
    except Exception, e:
        print e
        db.session.rollback()
        return 0
