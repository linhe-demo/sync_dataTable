#! /usr/bin/env python3
# 【数据拉取】运营-2022年销量及退货数量数据-花童和青年伴娘裙
from datetime import timedelta, datetime

from tools.dbLink import getAll

from tools.writeExcel import saveToExcel

from tools.showInfo import printLog

from sqlmap.salesSql import sqlmap

from tools.sendEmail import sendEmail


def getInfoByIds(bDate, eDate, paramList, fileName, filePath):
    printLog("拉取商品销量与退货数据", None)
    sheet1 = {}
    sheet2 = {}
    export1 = []
    export2 = []
    salesSql = ""
    refundSql = ""
    salesCondition = ()
    refundCondition = ()
    for i in paramList:
        if i.get("type") == 1:
            salesSql = sqlmap('getSalesBySize')
            refundSql = sqlmap('getRefundBySize')
            salesCondition = (i.get("color"), "','".join(i.get("size")), bDate, eDate, i.get("id"))
            refundCondition = (i.get("color"), "','".join(i.get("size")), bDate, eDate, i.get("id"))
        elif i.get("type") == 2:
            salesSql = sqlmap('getSalesById')
            refundSql = sqlmap('getRefundById')
            salesCondition = (bDate, eDate, i.get("id"))
            refundCondition = (bDate, eDate, i.get("id"))

        try:
            salesResults = getAll(salesSql, salesCondition)
            refundResults = getAll(refundSql, refundCondition)
            if i.get("sheet") == 1:
                for row in salesResults:
                    sheet1[row['size']] = {'Size': row['size'],
                                           '2022年销量': row['saleNum']}
                for row in refundResults:
                    if sheet1.get(row['size']) is None:
                        sheet1[row['size']] = {'Size': row['size'],
                                               '2022年销量': 0,
                                               '2022年退货数量': row['refund_num']}
                    else:
                        sheet1[row['size']]['2022年退货数量'] = row['refund_num']
            else:
                if i.get("type") == 1:
                    for row in salesResults:
                        sheet2[i.get("color") + row['size']] = {i.get("color") + ' Size': row['size'],
                                                                i.get("color") + ' 2022年销量': row['saleNum'],
                                                                i.get("color") + ' 2022年退货数量': 0}
                    for row in refundResults:
                        if (sheet2.get(i.get("color") + row['size'])).get(i.get("color") + ' 2022年退货数量') is None:
                            sheet2[i.get("color") + row['size']] = {i.get("color") + ' Size': row['size'],
                                                                    i.get("color") + ' 2022年销量': 0,
                                                                    i.get("color") + ' 2022年退货数量': row[
                                                                        'refund_num']}
                        else:
                            sheet2[i.get("color") + row['size']][i.get("color") + ' 2022年退货数量'] = row['refund_num']
                else:
                    for row in salesResults:
                        sheet2[row['color']] = {"销量排名前5的颜色": row['color'],
                                                "2022总销量": row['saleNum']}
        except Exception as e:
            raise e

    for k, v in sheet1.items():
        export1.append(v)
    target = 7
    num = 1
    for k, v in sheet2.items():
        if num <= 7:
            export2.append(v)
        else:
            mold = num % target
            for k1, v1 in v.items():
                export2[mold][k1] = v1
        num += 1

    # 写入excel
    saveToExcel({0: export1, 1: export2},
                {0: "206294-AS Picture", 1: "208588"},
                {0: ['Size', '2022年销量', '2022年退货数量'],
                 1: ['销量排名前5的颜色', '2022总销量', 'Dusty Blue Size', 'Dusty Blue 2022年销量', 'Dusty Blue 2022年退货数量',
                     'Blushing Pink Size', 'Blushing Pink 2022年销量', 'Blushing Pink 2022年退货数量', 'Ivory Size',
                     'Ivory 2022年销量', 'Ivory 2022年退货数量']},
                filePath)
    # sendEmail("商品销量与退货数据表", "商品销量与退货数据", ["muhe@kerrylan.com"], fileName, filePath, False)


if __name__ == "__main__":
    getInfoByIds("2022-01-01", "2022-12-31", [
        {"id": "206294", "color": "As Picture",
         "size": ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'], "type": 1, "sheet": 1},
        {"id": "208588", "color": "", "size": [], "type": 2, "sheet": 2},
        {"id": "208588", "color": "Dusty Blue", "size": ["J4", "J6", "J8", "J10", "J12", "J14", "J16"], "type": 1,
         "sheet": 2},
        {"id": "208588", "color": "Blushing Pink", "size": ["J4", "J6", "J8", "J10", "J12", "J14", "J16"], "type": 1,
         "sheet": 2},
        {"id": "208588", "color": "Ivory", "size": ["J4", "J6", "J8", "J10", "J12", "J14", "J16"], "type": 1,
         "sheet": 2}
    ], "GoodsSalesAndReturnInfo.xlsx", "../data/GoodsSalesAndReturnInfo.xlsx")
