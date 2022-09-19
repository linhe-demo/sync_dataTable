import json

import pandas as pd


def read_json_config():
    with open(r"D:\PythonProject\sync_dataTable\config\config.json") as json_file:
        config = json.load(json_file)
    return config


def read_excl(filePath):
    raw_data = pd.read_excel(filePath, header=0)  # header=0表示第一行是表头，就自动去除了
    return raw_data.values


def readRow(filePath, row):
    feature = []
    lists = []
    data = read_excl(filePath)  # 文件位置
    if row == 1:
        feature = data[:, 0:1]  # 取第一列
    elif row == 2:
        feature = data[:, 1:2]  # 取第二列

    m = 0
    for i in feature:
        tmpKey = str(feature[m][0])
        lists.append(tmpKey)
        m += 1
    return lists
