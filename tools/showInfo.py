
def printLog(msg, param):
    if param is not None:
        print(msg % param)
    else:
        print(msg)
