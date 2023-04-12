#! /usr/bin/env python3

# 【数据拉取】财务分析-退货物流收入数据2023.02 (oak-4566)
from tools.array import *
from tools.dbLink import getAll
from tools.readExcel import readExcelData

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.kll_sql.finanicalSql import sqlmap

from tools.sendEmail import sendEmail


def getReturnLogisticsRevenueByOrderSn(file, fileName, filePath):
    printLog("退货物流收入数据2023.02 开始拉取", None)
    exportData = []
    orderSn = readExcelData(file, 1)
    # 去除重复订单号
    tmpList = ArrayChunk(ArrayUnique(orderSn), 5000)
    num = 1
    for i in tmpList:
        printLog("第%s批数据 总数：%s", (num, len(i)))
        try:
            sql = sqlmap('getReturnLogisticsRevenueByOrderSn')
            results = getAll(sql, ("','".join(i)))
            for row in results:
                exportData.append({
                    'order_id': row['order_id'],
                    'refund_id': row['refund_id'],
                    'taobao_order_sn': row['taobao_order_sn'],
                    'r_status': row['r_status'],
                    'label_fee': row['label_fee'],
                    'currency': row['currency'],
                    'check_time': row['check_time'],
                    'label_fee_usd': row['label_fee_usd']
                })
        except Exception as e:
            raise e
        num += 1

    # 写入excel
    saveToExcel({0: exportData},
                {0: "明细"},
                {0: ['order_id', 'refund_id', 'taobao_order_sn', 'r_status', 'label_fee', 'currency', 'check_time',
                     'label_fee_usd']},
                filePath)
    sendEmail("数据报表", "退货退款数据", ["tansuan@kerrylan.com", "jjserppm@kerrylan.com"], fileName, filePath, False)


if __name__ == "__main__":
    getReturnLogisticsRevenueByOrderSn("../data/target.xlsx", 'returnLogisticsRevenue.xlsx',
                                       '../data/returnLogisticsRevenue.xlsx')
