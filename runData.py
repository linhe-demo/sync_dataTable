#! /usr/bin/env python3
import datetime
import decimal
import queue
import threading
import pymysql

ecshopList = queue.Queue()
erisList = queue.Queue()
mpsList = queue.Queue()
perflogList = queue.Queue()
priceTrackerList = queue.Queue()
reportYchenList = queue.Queue()
romeoList = queue.Queue()
tmptableList = queue.Queue()
vodkaList = queue.Queue()


def GetTableData(database):
    tableList = []
    db = dbConnection('origin', database)
    try:
        cursor = db.cursor()
        sql = "select table_name from information_schema.tables where table_schema = '%s' and table_type = 'base table'"
        cursor.execute(sql % database)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            tableList.append(row[0])
    except Exception as e:
        raise e

    return tableList


def DealTableData(dataBaseName):
    k = 1
    while k < 10:
        tt = MyThread(dataBaseName, k)
        tt.start()
        print("database " + dataBaseName + "thread " + str(k) + " start")
        k += 1


def InitList(tableList, dataBaseName):
    if dataBaseName == "ecshop":
        for i in tableList:
            ecshopList.put(i)
    elif dataBaseName == "eris":
        for i in tableList:
            erisList.put(i)
    elif dataBaseName == "mps":
        for i in tableList:
            mpsList.put(i)
    elif dataBaseName == "perflog":
        for i in tableList:
            perflogList.put(i)
    elif dataBaseName == "PRICE_TRACKER":
        for i in tableList:
            priceTrackerList.put(i)
    elif dataBaseName == "report_ychen":
        for i in tableList:
            reportYchenList.put(i)
    elif dataBaseName == "romeo":
        for i in tableList:
            romeoList.put(i)
    elif dataBaseName == "tmptable":
        for i in tableList:
            tmptableList.put(i)
    elif dataBaseName == "vodka":
        for i in tableList:
            vodkaList.put(i)


def dbConnection(type, database):
    if type == 'origin':
        db = pymysql.connect(host="10.193.51.71", database=database, user="root", password="123456")
    else:
        db = pymysql.connect(host="192.168.0.101", database=database, user="root", password="123456")
    return db


class MyThread(threading.Thread):
    """
    使用继承的方式实现多线程
    """

    def __init__(self, dataBaseName, num):
        super().__init__()  # 必须调用父类的构造方法
        self.dataBaseName = dataBaseName
        self.num = num

    def run(self):
        q = queue.Queue()
        if self.dataBaseName == "ecshop":
            q = ecshopList
        elif self.dataBaseName == "eris":
            q = erisList
        elif self.dataBaseName == "mps":
            q = mpsList
        elif self.dataBaseName == "perflog":
            q = perflogList
        elif self.dataBaseName == "PRICE_TRACKER":
            q = priceTrackerList
        elif self.dataBaseName == "report_ychen":
            q = reportYchenList
        elif self.dataBaseName == "romeo":
            q = romeoList
        elif self.dataBaseName == "tmptable":
            q = tmptableList
        elif self.dataBaseName == "vodka":
            q = vodkaList

        ndb = dbConnection('new', self.dataBaseName)
        odb = dbConnection('origin', self.dataBaseName)
        while not q.empty():
            tableName = q.get(timeout=5.0)
            try:
                cursor = odb.cursor()
                sql = "show create table %s.%s"
                cursor.execute(sql % (self.dataBaseName, tableName))
                # 获取所有记录列表
                results = cursor.fetchall()
                for row in results:
                    tmpTable = row[0]
                    createTableSql = row[1]
                    print("begin " + self.dataBaseName + " " + tmpTable)
                    # 检查表是否存在如果不存在则创建
                    checkTableExist(tmpTable, createTableSql, self.dataBaseName, ndb, odb)
            except Exception as e:
                raise e

        print("database " + self.dataBaseName + "thread " + str(self.num) + " end")


def checkTableExist(tmpTable, createTableSql, dataBase, ndb, odb):
    column = ""
    try:
        ocursor = odb.cursor()
        ncursor = ndb.cursor()
        # 检查新库中是否存在目标表
        sql = "select table_name from information_schema.TABLES t where t.TABLE_SCHEMA = '%s' and t.TABLE_NAME = '%s'"
        ncursor.execute(sql % (dataBase, tmpTable))
        results = ncursor.fetchone()
        if results is None:  # 如果不存在创建
            ncursor.execute(createTableSql)
            ndb.commit()

        # 获取目标表表中字段信息
        columnSql = "SELECT column_name FROM Information_schema.columns  WHERE TABLE_SCHEMA = '%s' and TABLE_NAME = '%s'"
        ocursor.execute(columnSql % (dataBase, tmpTable))
        cResults = ocursor.fetchall()
        for row in cResults:
            column += "`" + row[0] + "`,"
        column = column.strip(',')

        # 检查目标表中是否存在数据
        existSql = "SELECT COUNT(*) AS total FROM %s.%s "
        ncursor.execute(existSql % (dataBase, tmpTable))
        eResults = ncursor.fetchone()
        if eResults[0] > 70:  # 已存在数据不进行同步（如若需要同步可注释此处）
            print("%s %s Data synced" % (dataBase, tmpTable))
            return

        # 组装插入语句
        insertSql = "INSERT IGNORE INTO %s.%s (%s) VALUES"
        insertSql = insertSql % (dataBase, tmpTable, column)

        # 获取表中数据
        dataSql = "SELECT * FROM `%s`.`%s` "
        ocursor.execute(dataSql % (dataBase, tmpTable))
        results = ocursor.fetchall()
        for rowData in results:
            value = ""
            for data in rowData:
                data = transfer(data)  # 由于python中变量类型不是 str不能自接拼接需要转换为str
                # 检查返回值中是否包含引号
                if data.startswith("'b") is True:
                    value += "'no',"
                if data.startswith("'") is True or data.startswith('"') is True:
                    value += data + ","
                elif data.find('"') > -1 and data.find("'") > -1:
                    data = data.replace("'", "\\'")
                    value += "'" + data + "',"
                elif data.find('"') > -1:
                    if data.startswith('{"name"') is True and data.endswith('\\\'') is True:
                        value += "'" + data + "'',"
                    else:
                        value += "'" + data + "',"
                else:
                    value += '"' + data + '",'
            value = value.strip(',')
            tmpSql = insertSql + "(" + value + ")"
            res = ncursor.execute(tmpSql)
            if res == 0:
                print("fail " + tmpSql)
            else:
                ndb.commit()
    except Exception as e:
        raise e


def transfer(data):
    if data is None:
        data = ''
    elif type(data) == int:
        data = str(data)
    elif type(data) == datetime.datetime:
        data = str(data)
    elif type(data) == decimal.Decimal:
        data = str(data)
    elif type(data) == float:
        data = str(data)
    elif type(data) == datetime.date:
        data = str(data)
    elif type(data) == bytes:
        data = str(data)

    return data.strip()


if __name__ == "__main__":
    dataBases = ["ecshop", "eris", "mps", "perflog", "PRICE_TRACKER", "report_ychen", "romeo", "tmptable", "vodka"]
    for i in dataBases:
        tables = GetTableData(i)
        InitList(tables, i)
        DealTableData(i)
