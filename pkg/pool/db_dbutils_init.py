from dbutils.pooled_db import PooledDB
import pkg.pool.db_config as config

from pkg.pool.singleton import singleton


class MyConnectionPool(object):
    __pool = None

    def __init__(self):
        self.conn = self.__getconn()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.conn = self.__getconn()
        self.cursor = self.conn.cursor()

    def __getconn(self):
        if self.__pool is None:
            self.__pool = PooledDB(
                creator=config.DB_CREATOR,
                mincached=config.DB_MIN_CACHED,
                maxcached=config.DB_MAX_CACHED,
                maxshared=config.DB_MAX_SHARED,
                maxconnections=config.DB_MAX_CONNECYIONS,
                blocking=config.DB_BLOCKING,
                maxusage=config.DB_MAX_USAGE,
                setsession=config.DB_SET_SESSION,
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                passwd=config.DB_PASSWORD,
                db=config.DB_NAME,
                use_unicode=False,
                charset=config.DB_CHARSET
            )
        return self.__pool.connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def getcoon(self):
        conn = self.__getconn()
        cursor = conn.cursor()
        return cursor, conn


@singleton
def get_my_connection():
    return MyConnectionPool()
