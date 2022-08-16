#! /usr/bin/env python3 获取特定品类下的
import threading

from sqlmap.sqlone import sqlmap

from tools.dbLink import getAll


def Deal(cate, datatype):
    tt = MyThread(cate, datatype)
    tt.start()



class MyThread(threading.Thread):
    """
    使用继承的方式实现多线程
    """

    def __init__(self, cate, datatype):
        super().__init__()  # 必须调用父类的构造方法
        self.cate = cate
        self.datatype = datatype
        self.beginDate = "2021-01-01 00:00:00"
        self.endDate = "2021-12-31 23:59:59"

    def run(self):
        try:
            print("begin category：" + str(self.cate) + "dateType：" + self.datatype)
            sql = sqlmap(self.datatype)
            results = getAll(sql, (self.beginDate, self.endDate, self.cate))
            for row in results:
                print("Complete category calculation：" + str(self.cate) + "dateType：" + self.datatype, row)
        except Exception as e:
            raise e


if __name__ == "__main__":
    category = [2, 7, 8, 9, 10, 16, 17, 18, 22]
    for i in category:
        Deal(i, "ALL")  # 品类全部销量
        Deal(i, "16W-26W")  # 16W-26W尺寸 品类销量
        Deal(i, "customSize")  # 自定义尺寸 品类销量
