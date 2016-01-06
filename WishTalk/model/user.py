# -*- coding: utf-8 -*-
from server import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)
    is_blocked = db.Column(db.Boolean, nullable=False)


    def __init__(self, username, password, nickname='', avatar=''):
        self.username = username
        self.nickname = nickname or (u'用户'+username)
        self.password = password
        self.avatar = avatar or 'default.jpg'
        self.create_time = datetime.now()
        self.is_blocked = False

    def __repr__(self):
        return '<User %r>' % (self.username)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'is_blocked': self.is_blocked
        }

class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    gender = db.Column(db.String(10))
    grade = db.Column(db.String(10))
    school = db.Column(db.String(100))

    user = db.relationship('User', backref=db.backref('user_info', lazy='dynamic'))

    def __init__(self, user_id, gender='', grade='', school=''):
        self.user_id = int(user_id)
        self.gender = ''
        self.grade = ''
        self.school = ''

    def __repr__(self):
        return '<UserInfo user_id: %r>' % (self.user_id)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user.id,
            'username': self.user.username,
            'nickname': self.user.nickname,
            'gender': self.gender,
            'grade': self.grade,
            'school': self.school,
            'avatar': self.user.avatar,
            'is_blocked': self.user.is_blocked
        }

    def get_update_dict(self, kwargs):
        updateDict = {
            'gender': self.gender,
            'grade': self.grade,
            'school': self.school,
        }
        for k, v in updateDict.items():
            if kwargs.get(k):
                updateDict[k] = kwargs[k]
        return updateDict