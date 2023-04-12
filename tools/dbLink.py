# -*- coding: UTF-8 -*-
import pymysql

# 数据库信息
from tools.readFile import read_json_config

config = read_json_config()  # 获取配置信息


def dbConnection(group=None):
    if group == "wms":
        tmpConfig = config['db_wms']
        return pymysql.connect(host=tmpConfig['host'], port=tmpConfig['port'], database=tmpConfig['database'],
                               user=tmpConfig['user'],
                               password=tmpConfig['password'], connect_timeout=tmpConfig['timeout'])
    else:
        tmpConfig = config['db_powerful']
        return pymysql.connect(host=tmpConfig['host'], port=tmpConfig['port'], database=tmpConfig['database'],
                               user=tmpConfig['user'],
                               password=tmpConfig['password'], connect_timeout=tmpConfig['timeout'])


def getAll(sql, param, group=None):
    db = dbConnection(group)
    with db.cursor(cursor=pymysql.cursors.DictCursor) as conn:
        conn.execute(sql % param)
        res = conn.fetchall()
    return res


def getOne(sql, param, group=None):
    db = dbConnection(group)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql % param)
    return cursor.fetchone()
