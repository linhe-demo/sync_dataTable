# 单例模式函数，用来修饰类
def singleton(cls, *args, **kwargs):
    instances = {}

    def __singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return __singleton()
