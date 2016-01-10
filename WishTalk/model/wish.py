# -*- coding: utf-8 -*-

from server import db
from model.user import User
from datetime import datetime

class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    # 状态 unfinished:未完成 finishing:完成中 finished:完成 timeout:超时 closed:关闭
    status = db.Column(db.String(100), nullable=False)

    create_time = db.Column(db.DateTime, nullable=False)
    # 过期时间 格式"%Y-%m-%d %H:%M:%S" datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    out_time = db.Column(db.DateTime, nullable=False)
    # 完成时间
    finished_time = db.Column(db.DateTime, nullable=True)

    ctr = db.Column(db.Integer, nullable=False)    # 使用点击量来表示热度
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    helper_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE'), nullable=True)

    # 发起者
    owner = db.relationship('User', primaryjoin='User.id==Wish.owner_id', backref=db.backref('self_wishes', lazy='dynamic'))
    # 帮助者
    helper = db.relationship('User', primaryjoin='User.id==Wish.helper_id', backref=db.backref('help_wishes', lazy='dynamic'))

    def __init__(self, owner_id, title, content, out_time, location=""):
        self.owner_id = int(owner_id)
        self.title = title
        self.content = content
        self.location = location
        try:
            self.out_time =  datetime.strptime(out_time, "%Y-%m-%d %H:%M:%S")
        except Exception:
            self.out_time = datetime.strptime("2099-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.status = "unfinished"
        self.create_time = datetime.now()
        self.ctr = 0

    def __repr__(self):
        return '<Wish - %r: %r>' % (self.title, self.content)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'location': self.location,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'out_time': self.out_time.strftime("%Y-%m-%d %H:%M:%S"),
            'finished_time': self.finished_time.strftime("%Y-%m-%d %H:%M:%S") if self.finished_time else "",
            'status': self.status,
            'owner': self.owner.to_dict(),
            'helper': self.helper.to_dict() if self.helper else "",
            'ctr': self.ctr,
            'likers_count': self.likers.count(),
            'comment_count': self.comments.count()
        }

class WishLike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    wish_id = db.Column(db.Integer, db.ForeignKey('wish.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('like_wishs', lazy='dynamic'))
    wish = db.relationship('Wish', backref=db.backref('likers', lazy='dynamic'))

    def __init__(self, user_id, wish_id):
        self.user_id = int(user_id)
        self.wish_id = int(wish_id)
        self.create_time = datetime.now()

    def __repr__(self):
        return '<WishLike - user_id: %r, wish_id: %r>' % (self.user_id, self.wish_id)


class WishComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    wish_id = db.Column(db.Integer, db.ForeignKey('wish.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)

    wish = db.relationship('Wish', backref=db.backref('comments', lazy='dynamic'))
    user = db.relationship('User', primaryjoin='User.id==WishComment.user_id', backref=db.backref('comment_wishs', lazy='dynamic'))


    def __init__(self, user_id, wish_id, content):
        self.user_id = int(user_id)
        self.wish_id = int(wish_id)
        self.content = content
        self.create_time = datetime.now()

    def __repr__(self):
        return '<WishComment - user_id: %r, wish_id: %r, content: %r>' % (self.user_id, self.wish_id, self.content)

    def to_dict(self):
        return {    
            'id': self.id,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': self.content,
            'user': self.user.to_dict()
        }
