def sqlmap(index):
    sql = {
        "getReturnShippingFee": '''
            SELECT
                        r.ORDER_ID AS order_id,
                        FROM_UNIXTIME( UNIX_TIMESTAMP( r.CHECK_DATE_3 ), '%s' ),
                        romeo.convertCurrency_v2 ( eoi.currency, 'USD', r.ALTERATION_FEE, FROM_UNIXTIME( UNIX_TIMESTAMP( r.CHECK_DATE_3 ), '%s' ), 'USD' ) AS fee,
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
                        END AS r_status
            FROM
                        romeo.refund r
            INNER JOIN 
                        ecshop.ecs_order_info eoi ON eoi.order_id = r.ORDER_ID 
            WHERE
                        r.ORDER_ID IN ( '%s' ) 
            AND 
                        r.`STATUS` IN ('RFND_STTS_EXECUTED', 'RFND_STTS_INIT', 'RFND_STTS_IN_CHECK', 'RFND_STTS_CHECK_OK')
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
                        er.region_name,
                        r.CHECK_DATE_3 AS finishDate,
                        r.ALTERATION_FEE AS label,
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
            INNER JOIN 
                        ecshop.ecs_order_info eoi ON eoi.order_id = r.ORDER_ID
            INNER JOIN 
                        ecshop.ecs_region er on er.region_id=eoi.country
            INNER JOIN 
                        romeo.refund_detail rd ON rd.REFUND_ID = r.REFUND_ID
            INNER JOIN 
                        ecshop.ecs_order_goods eog ON eog.rec_id = rd.ORDER_GOODS_ID
            INNER JOIN 
                        ecshop.ecs_goods eg ON eg.goods_id = eog.goods_id
                WHERE
                        eg.goods_party_id = 65545
                        AND r.CREATED_STAMP >= '%s' 
                        AND r.CREATED_STAMP <= '%s' 
                        AND r.REFUND_TYPE_ID = 5 
                        AND r.`STATUS` IN ('RFND_STTS_EXECUTED', 'RFND_STTS_INIT', 'RFND_STTS_IN_CHECK', 'RFND_STTS_CHECK_OK')
                        ''',
        "getOrderInfo": '''
            SELECT
                        eoi.order_id,
                        eoi.taobao_order_sn,
                        er.region_name,
                        FROM_UNIXTIME( eoi.shipping_time, '%s' ) AS s_date,
                        romeo.convertCurrency_v2 ( eoi.currency, 'USD', eoi.shipping_fee, FROM_UNIXTIME( eoi.shipping_time, '%s' ), 'USD' ) AS t_shipping_fee,
                        eoi.shipping_fee AS o_shipping_fee,
                        eoi.order_amount AS o_order_amount,
                        romeo.convertCurrency_v2 ( eoi.currency, 'USD', eoi.order_amount, FROM_UNIXTIME( eoi.shipping_time, '%s' ), 'USD' ) AS t_order_amount,
                        eoi.currency,
                        eoi.duty_fee AS o_duty_fee,
                        romeo.convertCurrency_v2 ( eoi.currency, 'USD', eoi.duty_fee, FROM_UNIXTIME( eoi.shipping_time, '%s' ), 'USD' ) AS t_duty_fee,
                        eoe.vat_fee AS o_vat_fee,
                        romeo.convertCurrency_v2 ( eoi.currency, 'USD', eoe.vat_fee, FROM_UNIXTIME( eoi.shipping_time, '%s' ), 'USD' ) AS t_vat_fee,
                        CASE
                            eoi.`order_status` 
                            WHEN '0' THEN '未确认'
                            WHEN '1' THEN '已确认'
                            WHEN '2' THEN '已取消' 
                            WHEN '3' THEN '已无效' 
                            WHEN '4' THEN '已拒收'
                            WHEN '5' THEN '已完成'
                            WHEN '6' THEN '无货'
                            WHEN '7' THEN '补货'
                        END AS r_status
            FROM
                        ecshop.ecs_order_info eoi
            INNER JOIN 
                        ecshop.ecs_region er on er.region_id = eoi.country
            LEFT  JOIN
                        ecshop.ecs_order_extension eoe ON eoe.order_id = eoi.order_id
                WHERE
                        eoi.shipping_time >= UNIX_TIMESTAMP('%s')
                        AND eoi.shipping_time <= UNIX_TIMESTAMP('%s')
                        AND eoi.order_type_id='SALE'; 
        ''',
        "getReturnLogisticsRevenueByOrderSn": '''
            SELECT 
                        t.*, ROUND(romeo.convertCurrency(t.currency, 'USD', t.label_fee, t.check_time, 'USD'),2) AS label_fee_usd
            FROM (
                        SELECT      eoi.order_id, r.refund_id, 
                                    CONCAT("'", eoi.taobao_order_sn) AS taobao_order_sn,
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
                                    (0 - r.ALTERATION_FEE) as label_fee, 
                                    r.currency, 
                                    r.CHECK_DATE_1 AS check_time
                        FROM 
                                    ecshop.ecs_order_info eoi
                        LEFT JOIN 
                                    romeo.refund r ON r.order_id = CONVERT(eoi.order_id USING UTF8) AND r.`STATUS` IN ('RFND_STTS_EXECUTED', 'RFND_STTS_INIT', 'RFND_STTS_IN_CHECK', 'RFND_STTS_CHECK_OK')
                        WHERE 1
                        AND eoi.taobao_order_sn IN ('%s')
                ) AS t'''
    }
    return sql[index]
