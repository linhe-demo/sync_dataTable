# 检查列表中是否包含目标元素
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


# 将列表拆分成n个包含step个元素的列表的大列表
def ArrayChunk(lists, step):

    if len(lists) == 0:
        return []

    return [lists[i:i + step] for i in range(0, len(lists), step)]
