# -*- coding: UTF-8 -*-
import pymysql

# 数据库信息
from tools.readFile import read_json_config

config = read_json_config()  # 获取配置信息
config = config['db']


def dbConnection():
    return pymysql.connect(host=config['host'], port=config['port'], database=config['database'], user=config['user'],
                           password=config['password'], connect_timeout=config['timeout'])


def getAll(sql, param):
    db = dbConnection()
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql % param)
    return cursor.fetchall()


def getOne(sql, param):
    db = dbConnection()
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql % param)
    return cursor.fetchone()
