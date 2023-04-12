# script/orderInfo.py

import asyncio
import concurrent.futures
import time

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.kll_sql.finanicalSql import sqlmap

from tools.timeFormat import *

from pkg.pool.sqlpool import SqlPool

from tools.sendEmail import sendEmail

allDate = {}


async def main(tmpList, fileName, filePath):
    # tasks = [asyncio.create_task(testFunc(i)) for i in tmpList]
    # for n in tasks:
    #     print("here")
    #     await n
    # await asyncio.gather(*tasks)
    # tmpAll = sorted(allDate.items(), key=lambda x: x[0])

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        to_do = []
        for i in tmpList:
            future = executor.submit(getOrderInfo, i)
            to_do.append(future)

        for future in concurrent.futures.as_completed(to_do):
            future.result()

    m = 0
    data = {}
    desc = {}
    title = {}

    if allDate:
        for k, v in dict(allDate).items():
            data[m] = v
            desc[m] = "订单明细" + str(m + 1)
            title[m] = ['订单号', '淘宝订单号', '国家', '发货时间', '币种', '原始运费', '转换后运费', '原始订单金额', '转换后订单金额', '原始关税', '转换后关税',
                        '原始VAT增值税', '转换后VAT增值税', '订单状态']
            m += 1
        # 写入excel
        saveToExcel(data, desc, title, filePath)
        # sendEmail("数据报表", "订单信息", [""], filtansuan@kerrylan.comeName, filePath, True)
    else:
        printLog("暂无数据", None)


def testFunc(a):
    bDate = a[0]
    eDate = a[1]
    printLog("%s---%s订单数据开始拉取", (bDate, eDate))


def getOrderInfo(timeInfo):
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
