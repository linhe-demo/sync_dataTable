import time


class TokenBucket(object):

    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.currentAmount = 0
        self.lastConsumeTime = int(time.time())

    def consume(self, tokenAmount):
        timeDiff = (int(time.time()) - self.lastConsumeTime) * self.rate
        self.currentAmount = min(timeDiff + self.currentAmount, self.capacity)

        if tokenAmount > self.currentAmount:
            return False
        self.lastConsumeTime = int(time.time())
        self.currentAmount -= tokenAmount
        return True
