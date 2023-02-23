
def InArray(target, lists):
    res = False
    for i in lists:
        if target == i:
            res = True
            break

    return res


# 去除列表中重复的元素
def ArrayUnique(lists):
    tmpMap = {}
    newOrderSn = []
    for i in lists:
        if tmpMap.get(i) is None:
            newOrderSn.append(i)
            tmpMap[i] = 1

    return newOrderSn
