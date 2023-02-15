import hashlib
import json

from tools.getConfig import getConfigInfo


def signFunc(param):
    newParam = sorted(param.items(), key=lambda x: x[0])
    newDict = {}
    for k, v in newParam:
        newDict[k] = v
    tmpStr = str(json.dumps(newDict, separators=(',', ':')))
    tmpSignStr = "{}{}".format(tmpStr, getConfigInfo('erp_config')['appSecret'])

    m = hashlib.sha1()
    m.update(tmpSignStr.encode('utf-8'))

    return "{}.{}".format(getConfigInfo('erp_config')['appId'], m.hexdigest())
