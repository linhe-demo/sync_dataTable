import json

import requests

from tools.showInfo import printLog
from tools.sign import signFunc


def getErpStockInfo(url, method, time, param):
    # 生产函数签名
    sign = signFunc(param)
    res = requests.post(
        "{}{}?sign={}&time={}".format(url, method, sign, time),
        data=param, json=True)

    if len(res.content) == 0:
        printLog("暂无需要更新的数据", None)

    res = json.loads(res.content)
    if res.get('code') != 'OK':
        printLog("接口数据返回异常", None)
    else:
        return res.get('data')


def loginAccessories(url, method, param):
    headers = {'Content-Type': 'application/json'}
    res = requests.post("{}{}".format(url, method), data=json.dumps(param, separators=(',', ':')), headers=headers)
    if len(res.content) == 0:
        printLog("面辅料登录接口未返回登录数据", None)

    res = json.loads(res.content)
    if res.get('code') != 0:
        printLog("面辅料登录接口数据返回异常", None)
    else:
        return res.get('data')


def asyncAccessoriesStock(url, method, param, token):
    headers = {'Content-Type': 'application/json', 'authorization': token}
    res = requests.post("{}{}".format(url, method), data=json.dumps(param, separators=(',', ':')), headers=headers)
    if len(res.content) == 0:
        printLog("面辅料库存同步接口未返回登录数据", None)

    res = json.loads(res.content)
    if res.get('code') != 0:
        printLog("面辅料库存同步接口数据返回异常 %s", (res.get('msg')))
    else:
        return res.get('data')
