#! /usr/bin/env python3 获取批量收货的总计和明细
import pymysql

from sqlmap.sqlone import sqlmap

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel


def batchReceipt(beginDate, endDate, fileName):
    data = {}
    newData = {}
    exportTotalData = []
    exportDetailData = []

    sql = sqlmap('batchReceiptTotal')

    try:
        results = getAll(sql, (beginDate, endDate))
        # 将相同组织相同支付方式写入同一个list
        for row in results:
            index = row['组织名'] + "-" + str(row['支付id'])
            if index in data:
                data[index].append(row)
            else:
                data[index] = [row]
    except Exception as e:
        raise e
    # 排序
    for i, v in data.items():
        newData[i] = sorted(v, key=lambda k: k['导入时间'], reverse=True)

    # 每个组织每种支付方式只取最后三次批量收款记录
    for i, v in newData.items():
        if len(v) > 3:
            for s in v[:3]:
                exportTotalData.append(s)
        else:
            for s in v:
                exportTotalData.append(s)

    # 获取汇总数据中对应的明细数据
    for i in exportTotalData:
        sql = sqlmap('batchReceiptDetail')
        try:
            results = getAll(sql, i['明细id'])
            for row in results:
                exportDetailData.append(row)
        except Exception as e:
            raise e

    # 写入excel
    saveToExcel({0: exportTotalData, 1: exportDetailData},
                {0: "汇总", 1: "明细"},
                {0: ['明细id', '组织名', '支付id', '支付方式名', '导入人', '导入时间', '订单数量'],
                 1: ['明细id', '组织名', '支付id', '支付方式名', '导入人', '导入时间', '外部订单号', '收款金额']},
                fileName)


if __name__ == "__main__":
    batchReceipt('2021-05-01 00:00:00', '2021-05-10 23:59:59', '../data/batchReceipt.xlsx')  # 批量收货
