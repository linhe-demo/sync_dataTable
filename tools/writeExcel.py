import pandas as pd


def saveToExcel(fileData, sheetName, sheetTitle, fileName):
    writer = pd.ExcelWriter(fileName)
    for num in fileData:
        if len(fileData[num]) == 0:
            continue
        data = pd.DataFrame(fileData[num])
        data = data[sheetTitle[num]]
        data.to_excel(writer, sheetName[num], encoding='utf-8', index=False, header=True)

    writer.save()
    writer.close()

