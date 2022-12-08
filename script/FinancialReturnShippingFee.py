#! /usr/bin/env python3
# 财务分析-匹配对应的退货物流收入
from datetime import timedelta, datetime

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.finanicalSql import sqlmap

from tools.sendEmail import sendEmail


def financialReturnShippingFee(bDate, eDate, fileName, filePath):
    printLog("退货物流数据拉取", None)
    exportData = []
    # 获取满足条件的发货订单信息
    try:
        tmpOid = []
        tmpData = {}
        sql = sqlmap('getOrderInfoByShippingTime')
        results = getAll(sql, ('%Y-%m', bDate, eDate))
        for row in results:
            tmpOid.append(str(row['order_id']))
            tmpData[str(row['order_id'])] = {'订单号': row['taobao_order_sn'], '发货月份': row['date']}
    except Exception as e:
        raise e

    # 获取运费信息
    step = 5000
    tmpList = [tmpOid[i:i + step] for i in range(0, len(tmpOid), step)]
    for m in tmpList:
        try:
            sql = sqlmap('getReturnShippingFee')
            results = getAll(sql, ('%Y-%m-%d', '%Y-%m-01', "','".join(m)))
            for row in results:
                if tmpData.get(row['order_id']) is not None:
                    exportData.append({
                        '订单号': tmpData[row['order_id']]['订单号'],
                        '发货月份': tmpData[row['order_id']]['发货月份'],
                        '对应的退货物流收入': row['fee'],
                        '退款完成时间': row['finishDate']
                    })
        except Exception as e:
            raise e
    # 写入excel
    saveToExcel({0: exportData},
                {0: "明细"},
                {0: ['订单号', '发货月份', '对应的退货物流收入', '退款完成时间']},
                filePath)
    sendEmail("数据报表", "退货物流收入", ["tansuan@kerrylan.com"], fileName, filePath, True)


if __name__ == "__main__":
    financialReturnShippingFee("2022-08-01", "2022-10-01", 'financialReturnShippingFee.xlsx',
                               '../data/financialReturnShippingFee.xlsx')
