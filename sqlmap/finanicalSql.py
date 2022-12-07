def sqlmap(index):
    sql = {
        "getReturnShippingFee": '''
                SELECT
                            ORDER_ID as order_id,
	                        ALTERATION_FEE AS fee,
	                        CHECK_DATE_3 AS finishDate 
                FROM
	                        romeo.refund 
                WHERE
	                        ORDER_ID IN ('%s');
        ''',
        "getOrderInfoByShippingTime": '''
            SELECT
	                order_id,
	                taobao_order_sn,
	                FROM_UNIXTIME( shipping_time, '%s' ) AS date
            FROM
	                ecs_order_info 
            WHERE
	                shipping_time >= UNIX_TIMESTAMP('%s')
	        AND 
	                shipping_time < UNIX_TIMESTAMP('%s')
        '''
    }
    return sql[index]
