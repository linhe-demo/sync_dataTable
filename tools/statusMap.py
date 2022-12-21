
def saleOrderStatusMap(target):
    statusMap = {
        0: '未确认',
        1: '已确认',
        2: '取消',
        4: '拒收',
    }

    return statusMap.get(target, '暂无状态')


def shippingStatusMap(target):
    statusMap = {
        0: '待配货',
        1: '已发货',
        2: '收货确认',
        3: '拒收退回',
        4: '已发往自提点',
        5: '等待用户自提',
        6: '已自提',
        7: '自提取消',
        8: '已出库，待发货',
        9: '已配货，待出库',
        10: '已配货，但商品改变',
        11: '已追回',
    }

    return statusMap.get(target, '暂无状态')
