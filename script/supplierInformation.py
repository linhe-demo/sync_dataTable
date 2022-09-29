#! /usr/bin/env python3
# 鞋子、衣服配件、其他配件供应商收款信息拉取

import tools.readFile
from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.sqlone import sqlmap

from tools.sendEmail import sendEmail


def getSupplierInfo(categoryList, dressAccessoriesList, fileName, filePath):
    supplierInfo = []
    for i in categoryList:
        try:
            printLog("%s数据抽取中....", i)
            sql = sqlmap("getCategorySupplierInfo")
            results = getAll(sql, i)
            for row in results:
                supplierInfo.append(row)
        except Exception as e:
            raise e
    #  获取衣服配件供应商信息
    try:
        printLog("衣服配件数据抽取中....", None)
        sql = sqlmap("getDressAccessoriesSupplierInfo")
        results = getAll(sql, ("','".join(dressAccessoriesList)))
        for row in results:
            supplierInfo.append(row)
    except Exception as e:
        raise e

    # 写入excel
    saveToExcel({0: supplierInfo},
                {0: "明细"},
                {0: ['供应商CODE', '供应商名称', '收款人姓名', '手机号码', '身份证号码', '收款账号', '开户行', '银行联行号', '分类名']},
                filePath)
    # 发送邮件
    sendEmail("数据报表", "鞋子、衣服配件、其他配件供应商收款信息", ["tina.zhang@kerrylan.com"], fileName, filePath, False)


if __name__ == "__main__":
    getSupplierInfo(['鞋子', '其他配件'],
                    ['HLHS', 'SRYD', 'HXYD', 'yhpj', 'RJCPJ', 'DYQPJ', 'MJXPJ', 'LGXPJ', 'MTFS', 'MDLYPJ', 'bhj',
                     'ZHYD', 'MS'], "supplierInfo.xlsx", "../data/supplierInfo.xlsx")  # 获取 鞋子、衣服配件、其他配件供应商收款信息
