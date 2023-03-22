import time


class TokenBucket(object):
    """
        rate 每秒新增令牌数
        capacity 桶容量
    """
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.currentAmount = 0
        self.lastConsumeTime = int(time.time())
    """
        tokenAmount 需要的令牌数
    """
    def consume(self, tokenAmount):
        timeDiff = (int(time.time()) - self.lastConsumeTime) * self.rate
        self.currentAmount = min(timeDiff + self.currentAmount, self.capacity)

        if tokenAmount > self.currentAmount:
            return False
        self.lastConsumeTime = int(time.time())
        self.currentAmount -= tokenAmount
        return True
