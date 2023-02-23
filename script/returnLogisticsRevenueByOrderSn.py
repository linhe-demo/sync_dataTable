#! /usr/bin/env python3

# 【数据拉取】财务分析-退货物流收入数据2023.02 (oak-4566)
from tools.array import InArray, ArrayUnique
from tools.dbLink import getAll
from tools.readExcel import readExcelData

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.finanicalSql import sqlmap

from tools.sendEmail import sendEmail


def getReturnLogisticsRevenueByOrderSn(file, fileName, filePath):
    printLog("退货物流收入数据2023.02 开始拉取", None)
    exportData = []
    orderSn = readExcelData(file, 1)

    # 去除重复订单号
    orderSn = ArrayUnique(orderSn)

    step = 5000
    tmpList = [orderSn[i:i + step] for i in range(0, len(orderSn), step)]
    for i in tmpList:
        print(InArray('0116663105', i))
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
