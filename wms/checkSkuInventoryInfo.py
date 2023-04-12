# 获取sku的库存信息
#
from datetime import timedelta, datetime

from tools.array import ArrayUnique
from tools.dbLink import *
from tools.readFile import read_txt

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.wms_sql.inventorySql import sqlmap

from tools.sendEmail import sendEmail


def getInventoryInfo(file, fileName, filePath):
    printLog("开始读取需要分析的wms-sku信息", None)
    tmpTxt = read_txt(file)
    # 过滤文件中的sku
    skuMap = filterSku(tmpTxt)
    tmpPlanMap = {}
    inventoryMap = {}
    shipmentMap = {}
    remarkMap = {}
    excelData = []
    for k, v in skuMap.items():
        printLog("开始处理shipmentSn：%s, sku：%s", (k, v))

        for i in v:
            shipmentMap[i] = k

        # 获取sku的仓库信息
        try:
            sql = sqlmap('getWarehouseCodeBySku')
            results = getOne(sql, ("','".join(v), k), "wms")
            warehouseCode = results.get("warehouse_code", None)
            if warehouseCode is None:
                raise Exception("获取仓库code失败！" + ",".join(v))
        except Exception as e:
            raise e

        # 获取出库单计划出库数量
        try:
            sql = sqlmap('getShippingInfo')
            results = getAll(sql, (warehouseCode, "','".join(v)), "wms")
            for i in results:
                if tmpPlanMap.get(i.get('sku')) is None:
                    tmpPlanMap[i.get('sku')] = i.get('plan_quantity')
                else:
                    tmpPlanMap[i.get('sku')] += i.get('plan_quantity')
        except Exception as e:
            raise e

        # 获取库存信息
        try:
            sql = sqlmap('getInventoryInfo')
            results = getAll(sql, (warehouseCode, "','".join(v)), "wms")
            for i in results:
                if i.get('location_code') == '':
                    inventoryMap[i.get('sku')] = 0
                    remarkMap[i.get('sku')] = "真实库存是 %s 由于库位编码不存在被过滤".format(i.get('available_qty'))
                else:
                    inventoryMap[i.get('sku')] = i.get('available_qty')
        except Exception as e:
            raise e

    for k, v in tmpPlanMap.items():
        excelData.append({
            'sku': k,
            '发货单号': shipmentMap.get(k),
            '计划出库数量': v,
            '库存数量': inventoryMap.get(k, "暂无库存信息"),
            '备注': remarkMap.get(k, '')
        })

    # 写入excel
    saveToExcel({0: excelData},
                {0: "明细"},
                {0: ['sku', '发货单号', '计划出库数量', '库存数量', '备注']},
                filePath)
    # sendEmail("数据报表", "退货退款时效分析", ["muhe@kerrylan.com"], fileName, filePath, False)


def filterSku(tmpList):
    skuMap = {}
    for i in tmpList:
        if i[0].find("内容: shipmentSn :") > -1 and i[0].find(":当前sku "):
            index1 = i[0].find("OUT")
            index2 = i[0].find("[")
            index3 = i[0].find("]")
            shipmentSn = i[0][index1:index1+19]
            sku = i[0][index2+1:index3].strip("{").strip("}").split(",")

            for m in sku:
                if skuMap.get(shipmentSn, None) is not None:
                    skuMap[shipmentSn].append(m.strip(" "))
                else:
                    skuMap[shipmentSn] = [m.strip(" ")]

    if len(skuMap) > 0:
        for k, v in skuMap.items():
            skuMap[k] = ArrayUnique(v)
    return skuMap


if __name__ == "__main__":
    getInventoryInfo('../data/sku.txt', 'InventoryInfo.xlsx', '../data/InventoryInfo.xlsx')  # 获取库存信息
