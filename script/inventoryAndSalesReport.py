#! /usr/bin/env python3
# VV组织特定品类的skc库存及销量数据报表
from datetime import timedelta, datetime

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.sqlone import sqlmap


def inventoryAndSales(group, categoryList, fileName):
    allData = {}
    exportData = []
    for i in categoryList:
        printLog("开始品类%s数据抽取", i)
        # 获取品类下的sku数据
        tmpGid = []
        tmpData = {}
        try:
            sql = sqlmap('getCategorySku')
            results = getAll(sql, (group, i))
            # 拼装初始数据
            for row in results:
                tmpGid.append(str(row['external_goods_id']))
                tmpData[str(row['p_id']) + row['color']] = {'组织': 'VV', '品类': i, 'PID': row['p_id'], '颜色': row['color'],
                                                            '主id': str(row['master_goods_id'])}
        except Exception as e:
            raise e
        printLog("品类%s数据量：%s", (i, len(tmpGid)))
        # 获取国内，外 可预订量（共库存）小于等于6的数据 由于数量较大 分为5000一组进行读取
        step = 5000
        tmpList = [tmpGid[i:i + step] for i in range(0, len(tmpGid), step)]
        for m in tmpList:
            try:
                sql = sqlmap('getInventoryNumber')
                res = getAll(sql, "','".join(m))
                for row in res:
                    if tmpData.get(row['skey']) is not None:
                        allData[row['skey']] = {'组织': tmpData[row['skey']]['组织'],
                                                '品类': i,
                                                'PID': tmpData[row['skey']]['PID'],
                                                '颜色': tmpData[row['skey']]['颜色'],
                                                '主id': tmpData[row['skey']]['主id'],
                                                '国内可预订量': row['num'],
                                                '国外可预订量': row['numOverseas'],
                                                '过去14天销量': 0,
                                                '过去28天销量': 0,
                                                }
            except Exception as e:
                raise e
        # 获取sku的14,28天销量数据 由于数量较大 分为5000一组进行读取
        step = 5000
        tmpList = [tmpGid[i:i + step] for i in range(0, len(tmpGid), step)]
        start = datetime.now()
        days14 = start - timedelta(14)
        days28 = start - timedelta(28)
        printLog("销量14天起始时间：%s 销量28天起始时间：%s", (days14, days28))
        for m in tmpList:
            try:
                sql = sqlmap('getSalesData')
                results = getAll(sql, (days14, days28, group, days28, "','".join(m)))

                for row in results:
                    if len(allData.get(row['skey'], '')) > 0:
                        allData[row['skey']]['过去14天销量'] = row['day14Sales']
                        allData[row['skey']]['过去28天销量'] = row['day28Sales']
            except Exception as e:
                raise e
    for i in allData:
        if allData[i].get("国内可预订量", 0) + allData[i].get("国外可预订量", 0) <= 6:
            exportData.append(allData[i])
    # 写入excel
    saveToExcel({0: exportData},
                {0: "明细"},
                {0: ['组织', '品类', 'PID', '颜色', '主id', '国内可预订量', '国外可预订量', '过去14天销量', '过去28天销量']},
                fileName)


if __name__ == "__main__":
    inventoryAndSales(65594, [199, 1003, 1044, 202, 1045, 1001, 1002, 1038], '../data/inventorySales.xlsx')  # 获取库存销量数据
