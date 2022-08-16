import pandas as pd


def saveToExcel(fileData, sheetName, sheetTitle, fileName):
    writer = pd.ExcelWriter(fileName)
    num = 0
    for sy in range(0, len(fileData)):
        data = pd.DataFrame(fileData[num])
        data = data[sheetTitle[num]]
        data.to_excel(writer, sheetName[num], encoding='utf-8', index=False, header=True)
        num += 1
    writer.save()
    writer.close()
