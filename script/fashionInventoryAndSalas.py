#! /usr/bin/env python3
# JJS 轻礼服时装销量&入库数据拉取

from pkg.coroutine.dbCoroutine import consumeCoroutine
from tools.array import *
from tools.dbLink import getAll
from tools.sendEmail import sendEmail

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.kll_sql.lableSql import sqlmap


def getInventoryAndSalas(partyId, categoryId, fileName, filePath):
    tmpPsku = []
    tmpData = {}
    excelData = []

    #  获取组织品类下基础数据
    try:
        printLog("JJS组织（组织ID：%s）品类：%s 基础数据抽取中....", (partyId, categoryId))
        sql = sqlmap("JJSLightDressBaseData")
        results = getAll(sql, ("%Y-%m-%d", categoryId, partyId))
        for row in results:
            tmpData[row['PSKU']] = {'PSKU': row['PSKU'],
                                    'PID': row['PID'],
                                    'GID': row['GID'],
                                    '颜色': row['颜色'],
                                    '尺码': row['尺码'],
                                    'id最近一次上架时间': row['id最近一次上架时间'],
                                    'id首次上架时间': row['id首次上架时间'],
                                    'PSKU上架以来总销量': row['PSKU上架以来总销量'],
                                    'PSKU总入库数': 0,
                                    'PSKU当前国内可预订量': 0,
                                    'PSKU首次备货数': 0,
                                    'PSKU第二次备货数': 0,
                                    'PSKU第三次备货数': 0,
                                    'PSKU首次入库数': 0,
                                    'PSKU第二次入库数': 0,
                                    'PSKU第三次入库数': 0}
            tmpPsku.append(row['PSKU'])
    except Exception as e:
        raise e
    tmpPsku = ArrayUnique(tmpPsku)
    tmpList = ArrayChunk(tmpPsku, 5000)

    for m in tmpList:
        # 获取组织品类下可入库数据
        try:
            printLog("JJS组织（组织ID：%s）品类：%s 入库数据抽取中....", (partyId, categoryId))
            sql = sqlmap("JJSLightDressReceiptData")
            results = getAll(sql, ("','".join(m)))
            for row in results:
                if tmpData.get(row['PSKU']) is not None:
                    tmpData[row['PSKU']]['PSKU总入库数'] = row['入库数']
        except Exception as e:
            raise e

        # 获取组织品类下可预订量数据
        try:
            printLog("JJS组织（组织ID：%s）品类：%s 可预订量数据抽取中....", (partyId, categoryId))
            sql = sqlmap("JJSLightDressAvailableData")
            results = getAll(sql, ("','".join(m)))
            for row in results:
                if tmpData.get(row['PSKU']) is not None:
                    tmpData[row['PSKU']]['PSKU当前国内可预订量'] = row['可预定量']
        except Exception as e:
            raise e

    # 获取前三次备货数和入库数
    tmpData = consumeCoroutine(tmpPsku, tmpData, 30)

    for n in tmpData:
        excelData.append(tmpData[n])
    # 写入excel
    saveToExcel({0: excelData},
                {0: "明细"},
                {0: ['PSKU', 'PID', 'GID', '颜色', '尺码', 'id最近一次上架时间', 'id首次上架时间', 'PSKU上架以来总销量', 'PSKU总入库数',
                     'PSKU当前国内可预订量', 'PSKU首次备货数',
                     'PSKU第二次备货数',
                     'PSKU第三次备货数',
                     'PSKU首次入库数',
                     'PSKU第二次入库数',
                     'PSKU第三次入库数']},
                filePath)
    # 发送邮件
    sendEmail("数据报表", "JJS 轻礼服时装销量&入库数据报表", ["menglu@kerrylan.com", "tansuan@kerrylan.com"], fileName, filePath, True)


if __name__ == "__main__":

    getInventoryAndSalas(65545, 295, "jjsInventoryAndSalasInfo.xlsx",
                         "../data/jssInventoryAndSalasInfo.xlsx")  # JJS 轻礼服时装销量&入库数据拉取
