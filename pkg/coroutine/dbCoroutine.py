# 用于处理 数据量大（不存在相互影响）需要多协程消费的场景
import asyncio
import concurrent
import math

from pkg.tokenbucket.bucket import TokenBucket
from sqlmap.kll_sql.lableSql import sqlmap
from tools.array import ArrayChunk
from tools.dbLink import getAll
from tools.showInfo import printLog


def consumeCoroutine(data=None, tmpData=None, num=10, style=1):
    if data is None or tmpData is None:
        return tmpData

    # 根据启用的协程数分割数据
    step = math.ceil(len(data) / num)
    data = ArrayChunk(data, step)

    asyncio.run(dealData(num, data, tmpData, style))

    return tmpData


async def dealData(consumerNum, data, tmpData, style):
    # 开启令牌桶
    bucket = TokenBucket(30, 60)
    # 启用协程开始消费数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=consumerNum) as executor:
        to_do = []
        m = 1
        for i in data:
            if style == 1:  # JJS 轻礼服时装销量&入库数据
                future = executor.submit(asyncData, i, m, tmpData, bucket)
            else:
                pass
            to_do.append(future)
            m += 1

        for future in concurrent.futures.as_completed(to_do):
            future.result()


def asyncData(tmpPsku, cNum, tmpData, bucket):
    num = 1
    while len(tmpPsku) > 0:
        tmpSku = tmpPsku[0]
        if bucket.consume(1) is True:
            try:
                printLog(" 协程 %s 序号：%s PSKU %s 前三次备货数据抽取中....", (cNum, num, tmpSku))
                sql = sqlmap("JJSLightDressStockData")
                results = getAll(sql, tmpSku)
                tmpNum1 = 1
                for row in results:
                    if tmpData.get(row['PSKU']) is not None:
                        if tmpNum1 == 1:
                            tmpData[row['PSKU']]['PSKU首次备货数'] = row['备货数']
                        elif tmpNum1 == 2:
                            tmpData[row['PSKU']]['PSKU第二次备货数'] = row['备货数']
                        else:
                            tmpData[row['PSKU']]['PSKU第三次备货数'] = row['备货数']
                    tmpNum1 += 1
            except Exception as e:
                raise e

            try:
                printLog(" 协程 %s 序号：%s PSKU %s 前三次入库数据抽取中....", (cNum, num, tmpSku))
                sql = sqlmap("JJSLightDressReceiptThreeTimesData")
                results = getAll(sql, ("%Y-%m-%d", tmpSku))
                tmpNum2 = 1
                for row in results:
                    if tmpData.get(row['PSKU']) is not None:
                        if tmpNum2 == 1:
                            tmpData[row['PSKU']]['PSKU首次入库数'] = row['入库数']
                        elif tmpNum2 == 2:
                            tmpData[row['PSKU']]['PSKU第二次入库数'] = row['入库数']
                        else:
                            tmpData[row['PSKU']]['PSKU第三次入库数'] = row['入库数']
                        tmpNum2 += 1
            except Exception as e:
                raise e
            tmpPsku = tmpPsku[1:len(tmpPsku)]
            num += 1
