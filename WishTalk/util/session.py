# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://root:000ooo@localhost:3306/mm')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
session = DBSession()

