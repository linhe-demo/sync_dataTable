# script/multiCoroutineDataSync.py
# 支持单生产者，多消费者数据同步

import asyncio
import concurrent
import math
import time

from tools.curl import *
from tools.dbLink import getAll
from tools.getConfig import getConfigInfo
from tools.showInfo import printLog
from sqlmap.goodsSql import sqlmap


async def main(sourceType, data, consumerNum):
    productData = []
    if sourceType == 'sql':
        sql = sqlmap(data.get('key'))
        try:
            results = getAll(sql, (data.get('param').get('bDate'), data.get('param').get('eDate')))
            for row in results:
                productData.append(row)
        except Exception as e:
            raise e
    elif sourceType == 'curl':
        tmpTime = math.ceil(time.time())
        param = {"time": str(tmpTime), "start_at": data.get("param").get("start_at"),
                 "end_at": data.get("param").get('end_at'), "type": data.get("param").get('type')}

        productData = getErpStockInfo(getConfigInfo('erp_config')['url'], data.get('method'), time, param)

    # 对数据中的数据类型进行修复
    for i in range(len(productData)):
        productData[i]['quantity'] = float(productData[i].get('quantity'))

    # 计算每个协程需要消耗的数据量
    tmpLen = math.ceil(len(productData) / consumerNum)
    # 将生产数据分割为多个消费列表
    newProductData = [productData[i:i + tmpLen] for i in range(0, len(productData), tmpLen)]

    # 获取面辅料后端登录接口token
    client = loginAccessories(getConfigInfo('accessories_config')['url'], "/user/login",
                              {"username": getConfigInfo('accessories_config')['userName'],
                               "password": getConfigInfo('accessories_config')['password']})
    token = client.get('accessToken')

    # 启用协程开始消费数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=consumerNum) as executor:
        to_do = []
        m = 1
        for i in newProductData:
            future = executor.submit(asyncData, i, m, token)
            to_do.append(future)
            m += 1

        for future in concurrent.futures.as_completed(to_do):
            future.result()

        printLog("数据同步已完成！", None)


def asyncData(data, num, token=None):
    time.sleep(1)  # 休眠1秒
    printLog("协程 %s 开始同步数据", num)
    # 开始调用面辅料后端同步接口
    asyncAccessoriesStock(getConfigInfo('accessories_config')['url'], "/sync/goods/stock", {"items": data}, token)
    printLog("协程 %s 同步完成！", num)


if __name__ == "__main__":
    t = time.perf_counter()
    asyncio.run(main('curl', {'method': 'Apiv1/Lace/goods/inventory',
                              'param': {"start_at": "2022-01-01", "end_at": "2023-02-14", "type": "fabric"}}, 10))
    print(f'coast:{time.perf_counter() - t:.8f}s')
