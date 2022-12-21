#! 采购-2021&2022年色卡sku级别的销量数据 （oak-4146）
import pymysql

from sqlmap.salesSql import sqlmap

from tools.dbLink import getAll
from tools.sendEmail import sendEmail
from tools.showInfo import printLog

from tools.writeExcel import saveToExcel


def calculateColorCardSales(beginDate, endDate, factory, category, fileName, filePath):
    printLog("色卡销量数据拉取中", None)
    exportData = []

    sql = sqlmap('colorCardSales')

    try:
        results = getAll(sql, ("%Y-%m-%d", beginDate, endDate, factory, category))
        for row in results:
            exportData.append({
                '外部订单号': row['外部订单号'],
                '发货时间': row['发货时间'],
                '色卡个数': row['色卡个数'],
                '该订单具体的sku': row['该订单具体的sku']
            })
    except Exception as e:
        raise e
    # 写入excel
    saveToExcel({0: exportData},
                {0: "明细"},
                {0: ['外部订单号', '发货时间', '色卡个数', '该订单具体的sku']},
                filePath)

    sendEmail("数据报表", "色卡销量信息", ["cindy.hu@kerrylan.com"], fileName, filePath, False)


if __name__ == "__main__":
    calculateColorCardSales('2022-11-13 00:00:00', '2022-12-13 23:59:59', '30246773', '33', 'colorCardSales.xlsx', '../data/colorCardSales.xlsx')  # 色卡销量
