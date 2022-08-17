import json

import pandas as pd


def read_json_config():
    with open(r"D:\PythonProject\sync_dataTable\config\config.json") as json_file:
        config = json.load(json_file)
    return config


def read_excl(filePath):
    file_path = "r'" + filePath + "'"  # r对路径进行转义，windows需要
    raw_data = pd.read_excel(filePath, header=0)  # header=0表示第一行是表头，就自动去除了
    return raw_data.values
