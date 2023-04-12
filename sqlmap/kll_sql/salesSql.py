def sqlmap(index):
    sql = {
        "colorCardSales": '''
                SELECT
                            eoi.taobao_order_sn as 外部订单号,
                            eg.uniq_sku as 该订单具体的sku,
                            if (eoi.shipping_time = 0, '', FROM_UNIXTIME(eoi.shipping_time, '%s')) as 发货时间,
                            SUM( eog.goods_number ) AS 色卡个数,
                            eoi.order_status,
	                        eoi.shipping_status
                FROM
                            ecs_order_info eoi
                INNER JOIN 
                            ecs_order_goods eog ON eog.order_id = eoi.order_id
                INNER JOIN 
                            ecs_goods eg ON eog.goods_id = eg.goods_id 
                WHERE
                            eoi.order_time >= '%s' 
                            AND eoi.order_time <= '%s' 
                            AND eoi.facility_id = '%s' 
                            AND eg.external_cat_id = '%s'
                            AND eoi.order_type_id = 'SALE' 
                            GROUP BY eoi.taobao_order_sn, eg.uniq_sku
                ''',
        "getSalesBySize": '''
                SELECT
	                        replace(ega_size.attr_value, 'J', '') AS `size`,
                            SUM(eog.goods_number) AS saleNum
                FROM
	                        ecshop.ecs_order_info eoi
	            INNER JOIN 
	                        ecshop.ecs_order_goods eog ON eoi.order_id = eog.order_id
	            INNER JOIN 
	                        ecshop.ecs_goods eg ON eg.goods_id = eog.goods_id
	            INNER JOIN 
	                        ecshop.ecs_goods_attr ega_color ON ega_color.goods_id = eg.goods_id AND ega_color.attr_id = '3367' AND ega_color.attr_value = '%s'
	            INNER JOIN 
	                        ecshop.ecs_goods_attr ega_size ON ega_size.goods_id = eg.goods_id AND ega_size.attr_id = '3373' AND ega_size.attr_value IN ( '%s' )
                WHERE
	                        eoi.order_time > '%s' 
	            AND 
	                        eoi.order_time < '%s' 
	            AND 
	                        eoi.order_type_id = 'SALE' 
	            AND 
	                        eoi.order_status != '2' 
	            AND 
	                        eg.external_goods_id IN ( %s ) 
	            AND RIGHT ( eoi.email, 8 ) NOT IN ( 'i9i8.com', 'ylan.com' ) 
	            AND 
	                      ( eoi.email = 'SNSorder@tetx.com' OR RIGHT ( eoi.email, 8 ) != 'tetx.com' )  
                GROUP BY
	                        ega_size.attr_value
	            ORDER BY cast(`size` as UNSIGNED INTEGER) ASC''',
        "getRefundBySize": '''
                SELECT
	                        replace(ega_size.attr_value, 'J', '') AS `size`,
                            SUM( rd.goods_number ) AS refund_num
                FROM
	                        ecshop.ecs_order_info eoi
	            INNER JOIN 
	                        ecshop.ecs_order_goods eog ON eoi.order_id = eog.order_id
	            INNER JOIN 
	                        ecshop.ecs_goods eg ON eg.goods_id = eog.goods_id
	            INNER JOIN 
	                        ecshop.ecs_goods_attr ega_color ON ega_color.goods_id = eg.goods_id AND ega_color.attr_id = '3367' AND ega_color.attr_value = '%s'
	            INNER JOIN 
	                        ecshop.ecs_goods_attr ega_size ON ega_size.goods_id = eg.goods_id AND ega_size.attr_id = '3373' AND ega_size.attr_value IN ( '%s' )
	            LEFT JOIN 
	                        romeo.refund_detail rd ON rd.ORDER_GOODS_ID = eog.rec_id
	            LEFT JOIN 
	                        romeo.refund r ON r.REFUND_ID = rd.REFUND_ID AND r.STATUS = 'RFND_STTS_EXECUTED'
                WHERE
	                        eoi.order_time > '%s' 
	            AND 
	                        eoi.order_time < '%s' 
	            AND 
	                        eoi.order_type_id = 'SALE' 
	            AND 
	                        eoi.order_status != '2' 
	            AND 
	                        eg.external_goods_id IN ( %s ) 
	            AND RIGHT ( eoi.email, 8 ) NOT IN ( 'i9i8.com', 'ylan.com' ) 
	            AND 
	                      ( eoi.email = 'SNSorder@tetx.com' OR RIGHT ( eoi.email, 8 ) != 'tetx.com' )  
                GROUP BY
	                        ega_size.attr_value
	            ORDER BY cast(`size` as UNSIGNED INTEGER) ASC
        ''',
        "getSalesById": '''
                SELECT
	                        ega_color.attr_value AS color,
                            SUM(eog.goods_number) AS saleNum
                FROM
	                        ecshop.ecs_order_info eoi
	            INNER JOIN 
	                        ecshop.ecs_order_goods eog ON eoi.order_id = eog.order_id
	            INNER JOIN 
	                        ecshop.ecs_goods eg ON eg.goods_id = eog.goods_id
	            INNER JOIN 
	                        ecshop.ecs_goods_attr ega_color ON ega_color.goods_id = eg.goods_id AND ega_color.attr_id = '3367'
                WHERE
	                        eoi.order_time > '%s' 
	            AND 
	                        eoi.order_time < '%s' 
	            AND 
	                        eoi.order_type_id = 'SALE' 
	            AND 
	                        eoi.order_status != '2' 
	            AND 
	                        eg.external_goods_id IN ( %s ) 
	            AND RIGHT ( eoi.email, 8 ) NOT IN ( 'i9i8.com', 'ylan.com' ) 
	            AND 
	                      ( eoi.email = 'SNSorder@tetx.com' OR RIGHT ( eoi.email, 8 ) != 'tetx.com' )  
                GROUP BY
	                        ega_color.attr_value
	            ORDER BY 
	                        saleNum desc LIMIT 7
        ''',
        "getRefundById": '''
                SELECT
                            ega_color.attr_value AS color,
                            SUM(rd.goods_number ) refund_num
                FROM
                            ecshop.ecs_order_info eoi
                INNER JOIN 
                            ecshop.ecs_order_goods eog ON eoi.order_id = eog.order_id
                INNER JOIN 
                            ecshop.ecs_goods eg ON eg.goods_id = eog.goods_id
                INNER JOIN 
                            ecshop.ecs_goods_attr ega_color ON ega_color.goods_id = eg.goods_id AND ega_color.attr_id = '3367'
                LEFT JOIN 
                            romeo.refund_detail rd ON rd.ORDER_GOODS_ID = eog.rec_id
                LEFT JOIN 
                            romeo.refund r ON r.REFUND_ID = rd.REFUND_ID  AND r.STATUS = 'RFND_STTS_EXECUTED'
                WHERE
                            eoi.order_time > '%s' 
                AND 
                            eoi.order_time < '%s' 
                AND 
                            eoi.order_type_id = 'SALE' 
                AND 
                            eoi.order_status != '2' 
                AND 
                            eg.external_goods_id IN ( %s ) 
                AND RIGHT ( eoi.email, 8 ) NOT IN ( 'i9i8.com', 'ylan.com' ) 
                AND 
                          ( eoi.email = 'SNSorder@tetx.com' OR RIGHT ( eoi.email, 8 ) != 'tetx.com' )  
                GROUP BY
                            ega_color.attr_value
                ORDER BY 
                            refund_num desc LIMIT 7
            '''
    }
    return sql[index]
