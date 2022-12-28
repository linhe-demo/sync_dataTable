import calendar
import time
from datetime import date, datetime


def strToTimestamp(timeStr):
    if len(timeStr) > 10:
        return int(round(time.mktime(time.strptime(timeStr, "%Y-%m-%d %H:%M:%S"))))
    else:
        return int(round(time.mktime(time.strptime(timeStr, "%Y-%m-%d"))))


def datetimeToStr(dateTime):
    return datetime.strftime(dateTime, "%Y-%m-%d")


def strToDatetime(timeStr):
    if len(timeStr) > 10:
        return datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.strptime(timeStr, "%Y-%m-%d")


def timestampToStr(seconds, formatType):
    if formatType == 'month':
        return time.strftime("%Y-%m-%d", time.localtime(seconds))
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))


def getThisMonthLastDay(timeStr):
    year = datetime.strptime(timeStr, '%Y-%m-%d').year
    month = datetime.strptime(timeStr, '%Y-%m-%d').month
    day = calendar.monthrange(year, month)[1]  # 返回一个列表，第一个整数:代表本月起始星期数(0:星期一 ... 6:星期天) ,第二个整数:代表本月最后一天的日期数
    return datetime(year, month, day).date()


def addMonths(sourceDate, months):
    month = sourceDate.month - 1 + months
    year = sourceDate.year + month // 12
    month = month % 12 + 1
    day = min(sourceDate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
