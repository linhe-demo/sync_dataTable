# 用于处理大量数据（不存在相互影响）需要多协程消费的场景


def main(num=10, data=None):
    if data is None:
        return


