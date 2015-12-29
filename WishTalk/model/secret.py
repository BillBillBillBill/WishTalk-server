# -*- coding: utf-8 -*-

from server import db
from model.user import User
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr

class Secret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)
    ctr = db.Column(db.Integer, nullable=False)    # 使用点击量来表示热度
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('secrets', lazy='dynamic'))

    def __init__(self, user_id, topic, content):
        self.user_id = int(user_id)
        self.topic = topic
        self.content = content
        self.create_time = datetime.now()
        self.ctr = 0

    def __repr__(self):
        return '<Secret - %r: %r>' % (self.topic, self.content)

    def to_dict(self):
        return {
            'id': self.id,
            'topic': self.topic,
            'content': self.content,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'user': self.user.to_dict(),
            'ctr': self.ctr,
            'likers_count': self.likers.count(),
            'collect_count': self.collections.count(),
            'comment_count': self.comments.count()
        }

class SecretLike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    secret_id = db.Column(db.Integer, db.ForeignKey('secret.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('like_secrets', lazy='dynamic'))
    secret = db.relationship('Secret', backref=db.backref('likers', lazy='dynamic'))

    def __init__(self, user_id, secret_id):
        self.user_id = int(user_id)
        self.secret_id = int(secret_id)
        self.create_time = datetime.now()

    def __repr__(self):
        return '<SecretLike - user_id: %r, secret_id: %r>' % (self.user_id, self.secret_id)

class SecretCollect(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    secret_id = db.Column(db.Integer, db.ForeignKey('secret.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('collect_secrets', lazy='dynamic'))
    secret = db.relationship('Secret', backref=db.backref('collections', lazy='dynamic'))

    def __init__(self, user_id, secret_id):
        self.user_id = int(user_id)
        self.secret_id = int(secret_id)
        self.create_time = datetime.now()

    def __repr__(self):
        return '<SecretCollect - user_id: %r, secret_id: %r>' % (self.user_id, self.secret_id)

    def to_dict(self):
        return {
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'secret': self.secret.to_dict() if self.secret else None
        }

class SecretComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    at_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    secret_id = db.Column(db.Integer, db.ForeignKey('secret.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)

    secret = db.relationship('Secret', backref=db.backref('comments', lazy='dynamic'))
    user = db.relationship('User', primaryjoin='User.id==SecretComment.user_id', backref=db.backref('comment_secrets', lazy='dynamic'))
    at_user = db.relationship('User', primaryjoin='User.id==SecretComment.at_user_id', backref=db.backref('at_by_comment', lazy='dynamic'))

    def __init__(self, user_id, at_user_id, secret_id, content):
        self.user_id = int(user_id)
        self.at_user_id = int(at_user_id) if at_user_id else None
        self.secret_id = int(secret_id)
        self.content = content
        self.create_time = datetime.now()

    def __repr__(self):
        return '<SecretComment - user_id: %r, secret_id: %r, content: %r>' % (self.user_id, self.secret_id, self.content)

    def to_dict(self):
        return {    
            'id': self.id,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': self.content,
            'user': self.user.to_dict(),
            'at_user': self.at_user.to_dict() if self.at_user else None,
            'likers_count': self.likers.count()
        }

    def to_dict_with_abstract(self):
        return {
            'id': self.id,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': self.content,
            'user': self.user.to_dict(),
            'at_user': self.at_user.to_dict() if self.at_user else None,
            'likers_count': self.likers.count(),
            'type': 'secret',
            'brief': self.secret.content
        }

class SecretReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    secret_id = db.Column(db.Integer, db.ForeignKey('secret.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('report_secrets', lazy='dynamic'))
    secret = db.relationship('Secret', backref=db.backref('reports', lazy='dynamic'))

    def __init__(self, user_id, secret_id, content):
        self.user_id = int(user_id)
        self.secret_id = int(secret_id)
        self.content = content
        self.create_time = datetime.now()

    def __repr__(self):
        return '<SecretReport - user_id: %r, secret_id: %r, content: %r>' % (self.user_id, self.secret_id, self.content)

    def to_dict(self):
        return {    
            'id': self.id,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': self.content,
            'user': self.user.to_dict(),
            'secret': self.secret.to_dict()
        }

class SecretCommentLike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    secret_comment_id = db.Column(db.Integer, db.ForeignKey('secret_comment.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('like_secret_comment', lazy='dynamic'))
    secret_comment = db.relationship('SecretComment', backref=db.backref('likers', lazy='dynamic'))

    def __init__(self, user_id, secret_comment_id):
        self.user_id = int(user_id)
        self.secret_comment_id = int(secret_comment_id)
        self.create_time = datetime.now()

    def __repr__(self):
        return '<SecretCommentLike> - user_id: %r, secret_comment_id: %r>' % (self.user_id, self.secret_comment_id)