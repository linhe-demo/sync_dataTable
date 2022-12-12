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
            AND 
                        REFUND_TYPE_ID = 5
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
        ''',
        "getRefundDateInfo": '''
            SELECT
                    eoi.taobao_order_sn,
                    FROM_UNIXTIME( UNIX_TIMESTAMP( r.CREATED_STAMP ), '%s' ) AS r_date,
                    FROM_UNIXTIME( eoi.shipping_time, '%s' ) AS s_date,
                    r.CHECK_DATE_3 AS finishDate,
                    CASE
                        r.`STATUS` 
                        WHEN 'RFND_STTS_INIT' THEN
                        '新建' 
                        WHEN 'RFND_STTS_IN_CHECK' THEN
                        '审核' 
                        WHEN 'RFND_STTS_EXECUTED' THEN
                        '完成' 
                        WHEN 'RFND_STTS_CHECK_OK' THEN
                        '待退款' 
                    END AS r_status,
                    eg.external_cat_id
                FROM
                    romeo.refund r
                    INNER JOIN ecshop.ecs_order_info eoi ON eoi.order_id = r.ORDER_ID
                    INNER JOIN romeo.refund_detail rd ON rd.REFUND_ID = r.REFUND_ID
	                INNER JOIN ecshop.ecs_order_goods eog ON eog.rec_id = rd.ORDER_GOODS_ID
	                INNER JOIN ecshop.ecs_goods eg ON eg.goods_id = eog.goods_id
                WHERE
                    r.CREATED_STAMP >= '%s' 
                    AND r.CREATED_STAMP <= '%s' 
                    AND r.REFUND_TYPE_ID = 5 
                    AND r.`STATUS` IN ('RFND_STTS_EXECUTED', 'RFND_STTS_INIT', 'RFND_STTS_IN_CHECK', 'RFND_STTS_CHECK_OK')
                        '''
    }
    return sql[index]
