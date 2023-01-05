# pkg/pool/sqlpool.py

import pymysql
from dbutils.pooled_db import PooledDB
from tools.showInfo import printLog


from tools.readFile import read_json_config

config = read_json_config()  # 获取配置信息
config = config['db_powerful']

cfg = {
        'host': config['host'],
        'port': config['port'],
        'user': config['user'],
        'password': config['password'],
        'database': config['database'],
        'charset': 'utf8mb4',
        'maxconnections': 4,    # 连接池允许的最大连接数
        'mincached': 0,         # 初始化连接池时创建的连接数。默认为0，即初始化时不创建连接
        'maxcached': 0,         # 连接池中空闲连接的最大数量。默认0，即无最大数量限制
        'maxusage': 0,          # 连接的最大使用次数。默认0，即无使用次数限制
        'blocking': True        # 连接数达到最大时，新连接是否可阻塞。默认False，即达到最大连接数时，再取新连接将会报错
    }

# 重试
def auto_retry(func):
    def inner(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                printLog('执行异常  >>  {}  >>  {}'.format(func.__name__, e), None)

    return inner


class SqlPool:
    # mark为True, 查询语句的返回结果为dict
    def __init__(self, mark=False):
        self.pool = PooledDB(pymysql, **cfg)
        self.mark = mark

    # 获取连接，游标
    def get_conn_curs(self):
        conn = self.pool.connection()
        curs = conn.cursor(pymysql.cursors.DictCursor) if self.mark else conn.cursor()
        return conn, curs

    # 关闭游标，连接
    def close_conn_curs(self, curs, conn):
        curs.close()
        conn.close()

    # 执行sql
    @auto_retry
    def exe_sql(self, sql, args=None, way=None):
        conn, curs = self.get_conn_curs()
        try:
            curs.execute(sql, args=args)
            conn.commit()
        except Exception as e:
            conn.rollback()
            printLog("error  >>  exe_sql>  >>  {}".format(e), None)
            return False
        else:
            if way == 1:
                return curs.fetchone()
            elif way == 2:
                return curs.fetchall()
            else:
                return True
        finally:
            self.close_conn_curs(curs, conn)
