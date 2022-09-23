#! /usr/bin/env python3
# VV时装广东厂库存、VV时装广东样衣仓样衣单 数据脚本

import tools.readFile
from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.sqlone import sqlmap

from tools.sendEmail import sendEmail


def clearanceData(warehouseId, fileName, filePath):
    #  获取VV组织时装的所有品类id
    categoryList = []
    try:
        sql = sqlmap("getVVFashionCategoryId")
        results = getAll(sql, warehouseId)
        for row in results:
            categoryList.append(str(row['category_id']))
    except Exception as e:
        raise e

    if len(categoryList) == 0:
        printLog("暂无品类信息", "")
        return

    # 获取excel sku信息
    skuList = tools.readFile.readRow("../data/sku.xlsx", 1)
    if len(skuList) == 0:
        printLog("暂无sku信息", "")
        return

    printLog("sku总数：%s", len(skuList))
    table1 = []
    table2 = []
    table3 = []
    table4 = []
    step = 5000
    begin = 0
    tmpList = [skuList[i:i + step] for i in range(0, len(skuList), step)]
    for m in tmpList:
        printLog("前%s-%s SKU数据拉取", (begin, len(m) + begin))
        #  表1数据
        # try:
        #     printLog("表1数据抽取中....", None)
        #     sql = sqlmap('table-one')
        #     results = getAll(sql, ("','".join(m), "','".join(categoryList)))
        #     for row in results:
        #         table1.append(row)
        # except Exception as e:
        #     raise e

        #  表2数据
        try:
            printLog("表2数据抽取中....", None)
            sql = sqlmap('table-two')
            results = getAll(sql, ("','".join(m), "','".join(categoryList)))
            for row in results:
                table2.append(row)
        except Exception as e:
            raise e

        #  表3数据
        # try:
        #     sql = sqlmap('table-three')
        #     results = getAll(sql, ("','".join(m), "','".join(categoryList)))
        #     for row in results:
        #         table3.append(row)
        # except Exception as e:
        #     raise e

        begin += len(m)

    # 表4数据
    # for n in categoryList:
    #     try:
    #         printLog("品类：%s 表4数据抽取中....", n)
    #         sql = sqlmap('table-four')
    #         results = getAll(sql, n)
    #         for row in results:
    #             table4.append(row)
    #     except Exception as e:
    #         raise e

    # 写入excel
    saveToExcel({0: table1, 1: table2, 2: table3, 3: table4},
                {0: "表1", 1: "表2", 2: "表3", 3: "表4"},
                {0: ['PSKU', 'GSKU', 'PID', 'GID', '库存数量', '网站在架状态'],
                 1: ['PSKU', 'GSKU', 'PID', 'GID', '库存数量', '网站在架状态', '近1年销量', '近6个月销量', '近3个月销量', '近1个月销量'],
                 2: ['PSKU', 'GSKU', 'PID', 'GID', '库存SKU所属采购单号', '库存SKU所属采购单号剩余库存数量', '库存SKU所属采购单号下单时间', '库存SKU所属采购单号入库时间'],
                 3: ['样衣工单', '样衣ID', 'SKU', '样衣PID', '网站在架状态', '近1年销量', '近6个月销量', '近3个月销量', '近1个月销量']},
                filePath)
    # 发送邮件
    sendEmail("数据报表", "广东仓VV时装数据报表", ["tina.zhang@kerrylan.com"], fileName, filePath, False)


if __name__ == "__main__":
    clearanceData(2645, "clearance.xlsx", "../data/clearance.xlsx")  # 获取VV时装广东仓库存，样衣单数据
