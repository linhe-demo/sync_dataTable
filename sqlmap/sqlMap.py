def sqlmap(index):
    sql = {
        "getReturnShippingFee": '''
            SELECT * FROM table LIMIT 10
            '''
    }
    return sql[index]
