def sqlmap(index):
    sql = {
        "getReturnShippingFee": '''
            SELECT
                        r.ORDER_ID AS order_id,
                        FROM_UNIXTIME( UNIX_TIMESTAMP( r.CHECK_DATE_3 ), '%s' ),
                        romeo.convertCurrency_v2 ( eoi.currency, 'USD', r.ALTERATION_FEE, FROM_UNIXTIME( UNIX_TIMESTAMP( r.CHECK_DATE_3 ), '%s' ), 'USD' ) AS fee,
                        CHECK_DATE_3 AS finishDate 
            FROM
                        romeo.refund r
            INNER JOIN 
                        ecshop.ecs_order_info eoi ON eoi.order_id = r.ORDER_ID 
            WHERE
                        r.ORDER_ID IN ( '%s' ) 
            AND 
                        `STATUS` = 'RFND_STTS_EXECUTED'
            ''',
        "getOrderInfoByShippingTime": '''
            SELECT
	                order_id,
	                taobao_order_sn,
	                FROM_UNIXTIME( shipping_time, '%s' ) AS date,
	                currency
            FROM
	                ecs_order_info 
            WHERE
	                shipping_time >= UNIX_TIMESTAMP('%s')
	        AND 
	                shipping_time < UNIX_TIMESTAMP('%s')
        '''
    }
    return sql[index]
