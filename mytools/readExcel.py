from tools.readFile import read_excl

if __name__ == "__main__":
    data = read_excl("../data/demo.xlsx")  # 文件位置
    feature1 = data[:, 0:1]  # 取第一列
    feature2 = data[:, 1:2]  # 取第二列
    lists = []
    m = 0
    for i in feature1:
        tmpKey = str(feature1[m][0]) + feature2[m][0]
        lists.append(tmpKey)
        m += 1
    print("'" + "','".join(lists) + "'")
