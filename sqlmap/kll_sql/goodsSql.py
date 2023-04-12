def sqlmap(index):
    sql = {
        "getGidByOrderSn": '''  
                                SELECT 
                                            eoi.taobao_order_sn, 
                                            GROUP_CONCAT(DISTINCT eg.external_goods_id) AS goods_id
                                FROM
                                            ecshop.ecs_order_info eoi
                                INNER JOIN 
                                            ecshop.ecs_order_goods eog on eog.order_id=eoi.order_id
                                INNER JOIN
                                            ecshop.ecs_goods eg on eg.goods_id=eog.goods_id
                                WHERE
                                            eoi.taobao_order_sn IN ('%s')
                                GROUP BY    
                                            eoi.taobao_order_sn;
            ''',
    }
    return sql[index]
