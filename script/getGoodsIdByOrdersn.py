# script/orderInfo.py
# oak-4521【数据拉取】财务分析-拉取附件中订单号对应的商品gid


from tools.dbLink import getAll
from tools.readExcel import readExcelData

from tools.writeExcel import saveToExcel

from sqlmap.kll_sql.goodsSql import sqlmap

from tools.sendEmail import sendEmail

allDate = {}


def getGidByOrderSn(data, fileName, filePath):
    allData = []
    step = 5000
    tmpList = [data[i:i + step] for i in range(0, len(data), step)]
    for m in tmpList:
        sql = sqlmap('getGidByOrderSn')
        try:
            results = getAll(sql, ("','".join(m)))
            for row in results:
                allData.append({
                    '外部订单号': row['taobao_order_sn'],
                    '商品ID': row['goods_id']
                })
        except Exception as e:
            raise e
        print(len(allData))
    # 写入excel
    saveToExcel({0: allData},
                {0: "订单ID明细"},
                {0: ['外部订单号', '商品ID']},
                filePath)
    # 发送邮件
    sendEmail("数据报表", "商品ID明细表", ["shandai@kerrylan.com", "jjserppm@kerrylan.com"], fileName, filePath, False)


if __name__ == "__main__":
    tmpData = readExcelData("../data/orderSn.xlsx", 1)
    getGidByOrderSn(tmpData, "GoodsId.xlsx", "../data/GoodsId.xlsx")
