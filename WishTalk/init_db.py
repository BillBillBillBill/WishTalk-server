# -*- coding: utf-8 -*-

from model import *

from server import db

db.create_all()

db.session.commit()
