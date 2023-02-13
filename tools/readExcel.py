import json

import pandas as pd

from tools.readFile import read_excl


def readExcelData(filePath, column):
    data = read_excl(filePath)  # 文件位置
    feature1 = data[:, column-1:column]
    lists = []
    m = 0
    for i in feature1:
        tmpKey = str(feature1[m][0])
        lists.append(tmpKey)
        m += 1
    return lists

