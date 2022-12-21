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
                '''
    }
    return sql[index]
