#! /usr/bin/env python3
# VV组织特定品类的skc库存及销量数据报表
from datetime import timedelta, datetime

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from sqlmap.sqlone import sqlmap

from tools.sendEmail import sendEmail


def inventoryAndSales(group, categoryList, fileName):
    allData = {}
    exportData = []
    for i in categoryList:
        print("开始品类" + str(i) + "数据抽取")
        # 获取品类下的sku数据
        tmpSku = []
        tmpData = {}
        newData = {}
        salesSku = []
        try:
            sql = sqlmap('getCategorySku')
            results = getAll(sql, (group, i))
            # 拼装初始数据
            for row in results:
                tmpSku.append(row['uniq_sku'])
                tmpData[row['uniq_sku']] = {'组织': 'VV', '品类': i, 'PID': row['p_id'], '颜色': row['color'],
                                            '主id': row['external_goods_id']}
        except Exception as e:
            raise e
        # 获取国内sku共库存数小于等于6的sku由于数量较大 分为5000一组进行读取
        step = 5000
        tmpList = [tmpSku[i:i + step] for i in range(0, len(tmpSku), step)]
        for m in tmpList:
            try:
                sql = sqlmap('getInventoryNumber')
                res = getAll(sql, ("','".join(m), ",".join(['30246773', '369258324'])))
                for row in res:
                    if len(tmpData.get(row['uniq_sku'], '')) > 0:
                        newData[row['uniq_sku']] = {'组织': tmpData[row['uniq_sku']]['组织'],
                                                    '品类': i,
                                                    'PID': tmpData[row['uniq_sku']]['PID'],
                                                    '颜色': tmpData[row['uniq_sku']]['颜色'],
                                                    '主id': tmpData[row['uniq_sku']]['主id'],
                                                    '国内可预订量': row['available'],
                                                    '国外可预订量': 0,
                                                    '过去14天销量': 0,
                                                    '过去28天销量': 0,
                                                    }
                        salesSku.append(row['uniq_sku'])
            except Exception as e:
                raise e
        # 获取国外sku共库存数小于等于6的sku由于数量较大 分为5000一组进行读取
        step = 5000
        tmpList = [tmpSku[i:i + step] for i in range(0, len(tmpSku), step)]
        for m in tmpList:
            try:
                sql = sqlmap('getInventoryNumber')
                results = getAll(sql, ("','".join(m), ",".join(
                    ['1541849840', '1613991211', '1049275062', '1049275063', '2640152423', '2710948373',
                     '2771772189'])))
                for row in results:
                    if len(tmpData.get(row['uniq_sku'], '')) > 0:
                        if len(newData.get(row['uniq_sku'], '')) > 0:
                            newData[row['uniq_sku']]['国外可预订量'] = row['available']
                        else:
                            newData[row['uniq_sku']] = {'组织': tmpData[row['uniq_sku']]['组织'],
                                                        '品类': i,
                                                        'PID': tmpData[row['uniq_sku']]['PID'],
                                                        '颜色': tmpData[row['uniq_sku']]['颜色'],
                                                        '主id': tmpData[row['uniq_sku']]['主id'],
                                                        '国内可预订量': 0,
                                                        '国外可预订量': row['available'],
                                                        '过去14天销量': 0,
                                                        '过去28天销量': 0,
                                                        }
                            salesSku.append(row['uniq_sku'])
            except Exception as e:
                raise e
        # 获取sku的14,28天销量数据 由于数量较大 分为5000一组进行读取
        step = 5000
        salesList = [salesSku[i:i + step] for i in range(0, len(salesSku), step)]
        start = datetime.now()
        days14 = start - timedelta(14)
        days28 = start - timedelta(28)
        print("销量14天起始时间：" + str(days14))
        print("销量28天起始时间：" + str(days28))
        for m in salesList:
            try:
                sql = sqlmap('getSalesData')
                results = getAll(sql, (days14, days28, days28, "','".join(m)))

                for row in results:
                    if len(newData.get(row['uniq_sku'], '')) > 0:
                        newData[row['uniq_sku']]['过去14天销量'] = row['day14Sales']
                        newData[row['uniq_sku']]['过去28天销量'] = row['day28Sales']
            except Exception as e:
                raise e
        # 按照pskc分组
        for m in newData:
            index = str(newData[m].get('PID')) + "-" + str(newData[m].get('主id')) + newData[m].get('颜色')
            if len(allData.get(index, '')) > 0:
                allData[index] = {'组织': allData[index]['组织'],
                                  '品类': allData[index]['品类'],
                                  'PID': allData[index]['PID'],
                                  '颜色': allData[index]['颜色'],
                                  '主id': allData[index]['主id'],
                                  '国内可预订量': allData[index]['国内可预订量'] + newData[m].get('国内可预订量'),
                                  '国外可预订量': allData[index]['国外可预订量'] + newData[m].get('国外可预订量'),
                                  '过去14天销量': allData[index]['过去14天销量'] + newData[m].get('过去14天销量'),
                                  '过去28天销量': allData[index]['过去28天销量'] + newData[m].get('过去28天销量'),
                                  }
            else:
                allData[index] = newData[m]
    for i in allData:
        exportData.append(allData[i])
    # 写入excel
    saveToExcel({0: exportData},
                {0: "明细"},
                {0: ['组织', '品类', 'PID', '颜色', '主id', '国内可预订量', '国外可预订量', '过去14天销量', '过去28天销量']},
                fileName)
    sendEmail('from@runoob.com', ['296110717@qq.com'], '../data/inventorySales.xlsx')


if __name__ == "__main__":
    inventoryAndSales(65594, [199, 1003, 1044, 202, 1045, 1001, 1002, 1038], '../data/inventorySales.xlsx')  # 获取库存销量数据
