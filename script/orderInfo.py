# script/orderInfo.py


import asyncio
import datetime
import time

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.finanicalSql import sqlmap

from tools.timeFormat import *

from tools.sendEmail import sendEmail

allDate = {}


async def main(tmpList, fileName, filePath):
    tasks = [asyncio.create_task(getOrderInfo(i)) for i in tmpList]
    for n in tasks:
        await n

    tmpAll = sorted(allDate.items(), key=lambda x: x[0])
    m = 0
    data = {}
    desc = {}
    title = {}
    for k, v in dict(tmpAll).items():
        data[m] = v
        desc[m] = "订单明细" + str(m + 1)
        title[m] = ['订单号', '淘宝订单号', '国家', '发货时间', '币种', '原始运费', '转换后运费', '原始订单金额', '转换后订单金额', '原始关税', '转换后关税',
                    '原始VAT增值税', '转换后VAT增值税', '订单状态']
        m += 1
    # 写入excel
    saveToExcel(data, desc, title, filePath)
    sendEmail("数据报表", "订单信息", ["tansuan@kerrylan.com"], fileName, filePath, True)


async def getOrderInfo(timeInfo):
    bDate = timeInfo[0]
    eDate = timeInfo[1]
    printLog("%s---%s订单数据开始拉取", (bDate, eDate))
    exportData = []
    # 获取满足条件的发货订单信息
    try:
        sql = sqlmap('getOrderInfo')
        results = getAll(sql, ('%Y-%m-%d', '%Y-%m-%d', '%Y-%m-%d', '%Y-%m-%d', '%Y-%m-%d', bDate, eDate))
        for row in results:
            exportData.append({
                '订单号': row['order_id'],
                '淘宝订单号': row['taobao_order_sn'],
                '国家': row['region_name'],
                '发货时间': row['s_date'],
                '币种': row['currency'],
                '原始运费': row['o_shipping_fee'],
                '转换后运费': row['t_shipping_fee'],
                '原始订单金额': row['o_order_amount'],
                '转换后订单金额': row['t_order_amount'],
                '原始关税': row['o_duty_fee'],
                '转换后关税': row['t_duty_fee'],
                '原始VAT增值税': row['o_vat_fee'],
                '转换后VAT增值税': row['t_vat_fee'],
                '订单状态': row['r_status']
            })
    except Exception as e:
        raise e
    allDate[strToTimestamp(bDate)] = exportData
    printLog("%s---%s订单数据拉取结束", (bDate, eDate))


if __name__ == "__main__":
    bDate = '2022-01-01 00:00:00'
    eDate = '2022-12-31 23:59:59'
    t = time.perf_counter()
    tmpBDate = strToTimestamp(bDate)
    tmpEDate = strToTimestamp(eDate)
    dateList = []
    while tmpBDate < tmpEDate:
        tmpStr = timestampToStr(tmpBDate, 'month')
        tmpEnd = getThisMonthLastDay(tmpStr)
        tmpBDate = strToTimestamp(datetimeToStr(addMonths(strToDatetime(tmpStr), 1)))
        dateList.append([tmpStr + " 00:00:00", datetimeToStr(tmpEnd) + " 23:59:59"])
    asyncio.run(main(dateList, 'orderInfo.xlsx', '../data/orderInfo.xlsx'))
    print(f'coast:{time.perf_counter() - t:.8f}s')
