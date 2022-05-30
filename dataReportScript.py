#! /usr/bin/env python3
import pymysql

import pandas as pd


def dbConnection():
    return pymysql.connect(host="120.55.52.126", port=55190, database="ecshop", user="erpteamtemp",
                           password="erpteamtemp", connect_timeout=3600)


def save_to_excel(totalData, detailData):
    sheetName = {1: "汇总", 2: "明细"}
    sheetData = {1: totalData, 2: detailData}
    sheetTitle = {1: ['task_id', 'party_name', 'pay_id', 'pay_name', 'user_name', 'create_time', 'total'],
                  2: ['task_id', 'party_name', 'pay_id', 'pay_name', 'user_name', 'create_time', 'taobao_order_sn',
                      'received_amount']}
    writer = pd.ExcelWriter('data.xlsx')
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
                        pt.task_id,
                        IFNULL(pf.party_name, eoi.party_id) as party_name,
                        eoi.pay_id,
                        ep.pay_name,
                        pt.user_name,
                        pt.create_time,
                        count( eoi.order_id ) AS total 
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
                        pt.task_id,
                        IFNULL(pf.party_name, eoi.party_id) as party_name,
                        eoi.pay_id,
                        ep.pay_name,
                        pt.user_name,
                        pt.create_time,
                        ptd.taobao_order_sn,
                        ptd.received_amount
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


def batchReceipt(begindate, enddate):
    data = {}
    newData = {}
    exportTotalData = []
    exportDetailData = []

    db = dbConnection()
    sql = sqlmap('batchReceiptTotal')

    try:
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql % (begindate, enddate))
        results = cursor.fetchall()
        # 将相同组织相同支付方式写入同一个list
        for row in results:
            index = row['party_name'] + "-" + str(row['pay_id'])
            if index in data:
                data[index].append(row)
            else:
                data[index] = [row]
    except Exception as e:
        raise e
    # 排序
    for i, v in data.items():
        newData[i] = sorted(v, key=lambda k: k['create_time'], reverse=True)

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
            cursor.execute(sql % i['task_id'])
            results = cursor.fetchall()
            for row in results:
                exportDetailData.append(row)
        except Exception as e:
            raise e

    # 写入excel
    save_to_excel(exportTotalData, exportDetailData)


if __name__ == "__main__":
    batchReceipt('2021-01-01 00:00:00', '2021-10-1 23:59:59')  # 批量收货
