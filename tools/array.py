

def InArray(target, lists):
    res = False
    for i in lists:
        if target == i:
            res = True
            break

    return res
