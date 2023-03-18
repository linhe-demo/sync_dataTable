import pandas as pd

from tools.readFile import read_excl


# 读取excel中指定列整列元素，返回一个集合
def readExcelData(filePath, column):
    df = pd.read_excel(filePath, usecols=[column - 1])  # 指定读取的列
    df_list = df.values.tolist()
    backList = []
    for i in df_list:
        backList.append(i[0])

    if len(backList) == 0:
        data = read_excl(filePath)  # 文件位置
        feature1 = data[:, column - 1:column]
        m = 0
        for i in feature1:
            tmpKey = str(feature1[m][0])
            backList.append(tmpKey)
            m += 1
    else:
        return backList
