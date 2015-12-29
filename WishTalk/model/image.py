#coding:utf-8
from server import db
from datetime import datetime



class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)  # 创建时间

    def __init__(self, filename):
        self.filename = filename
        self.create_time = datetime.now()

    def __repr__(self):
        return '<Image - filename:%r >' % self.filename

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
