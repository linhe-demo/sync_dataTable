#! /usr/bin/env python3
import pymysql

import pandas as pd


def dbConnection():
    return pymysql.connect(host="****", port=0000, database="***", user="***",
                           password="***", connect_timeout=3600)


def saveToExcel(totalData, detailData, fileName):
    sheetName = {1: "汇总", 2: "明细"}
    sheetData = {1: totalData, 2: detailData}
    sheetTitle = {1: ['明细id', '组织名', '支付id', '支付方式名', '导入人', '导入时间', '订单数量'],
                  2: ['明细id', '组织名', '支付id', '支付方式名', '导入人', '导入时间', '外部订单号', '收款金额']}
    writer = pd.ExcelWriter(fileName)
    num = 0
    for sy in range(0, 2):
        num = num + 1
        data = pd.DataFrame(sheetData[num])
        data = data[sheetTitle[num]]
        data.to_excel(writer, sheetName[num], encoding='utf-8', index=False, header=True)

    writer.save()
    writer.close()


def sqlmap(index):
    sql = {
        'batchReceiptTotal': '''
             SELECT
                        pt.task_id as '明细id',
                        IFNULL(pf.party_name, eoi.party_id) as '组织名',
                        eoi.pay_id as '支付id',
                        ep.pay_name as '支付方式名',
                        pt.user_name as '导入人',
                        pt.create_time as '导入时间',
                        count( eoi.order_id ) as '订单数量' 
             FROM
                        payment_task pt
             INNER JOIN 
                        payment_task_detail ptd ON pt.task_id = ptd.task_id
             INNER JOIN 
                        ecs_order_info eoi ON eoi.taobao_order_sn = ptd.taobao_order_sn
             INNER JOIN 
                        ecs_payment ep ON eoi.pay_id = ep.pay_id
             LEFT JOIN 
                        romeo.party_facility pf ON pf.party_id = eoi.party_id
             WHERE
                        pt.create_time >= '%s' 
             AND    
                        pt.create_time <= '%s' 
             GROUP BY
	                    eoi.party_id, eoi.pay_id, pt.create_time''',

        'batchReceiptDetail': '''
             SELECT
                        pt.task_id as '明细id',
                        IFNULL(pf.party_name, eoi.party_id) as '组织名',
                        eoi.pay_id as '支付id',
                        ep.pay_name as '支付方式名',
                        pt.user_name as '导入人',
                        pt.create_time as '导入时间',
                        ptd.taobao_order_sn as '外部订单号',
                        ptd.received_amount as '收款金额'
             FROM
                        payment_task pt
             INNER JOIN 
                        payment_task_detail ptd ON pt.task_id = ptd.task_id
             INNER JOIN 
                        ecs_order_info eoi ON eoi.taobao_order_sn = ptd.taobao_order_sn
             INNER JOIN 
                        ecs_payment ep ON eoi.pay_id = ep.pay_id
             LEFT JOIN 
                        romeo.party_facility pf ON pf.party_id = eoi.party_id
             WHERE
                        pt.task_id = %s
             GROUP BY 
						ptd.abs_id   LIMIT 100'''
    }
    return sql[index]


def batchReceipt(beginDate, endDate, fileName):
    data = {}
    newData = {}
    exportTotalData = []
    exportDetailData = []

    db = dbConnection()
    sql = sqlmap('batchReceiptTotal')

    try:
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql % (beginDate, endDate))
        results = cursor.fetchall()
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
            cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute(sql % i['明细id'])
            results = cursor.fetchall()
            for row in results:
                exportDetailData.append(row)
        except Exception as e:
            raise e

    # 写入excel
    saveToExcel(exportTotalData, exportDetailData, fileName)


if __name__ == "__main__":
    batchReceipt('2021-05-01 00:00:00', '2021-05-10 23:59:59', './data/batchReceipt.xlsx')  # 批量收货
