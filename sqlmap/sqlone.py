def sqlmap(index):
    sql = {
        'getCategorySku': ''' /*获取品类下的sku信息*/
             SELECT 
                        eg.external_goods_id, eg.uniq_sku, ega.attr_value AS color, egm.p_id
             FROM 
                        ecshop.ecs_goods eg 
             INNER JOIN
	                    ecshop.ecs_goods_attr ega ON ega.goods_id = eg.goods_id AND ega.attr_id = '3367' -- goodsStyle_color
	         INNER JOIN 
	                    ecshop.ecs_goods_mapping egm ON eg.uniq_sku = egm.uniq_sku
             WHERE
                        eg.goods_party_id = %s 
             AND 
                        eg.external_cat_id = %s''',

        'getInventoryNumber': ''' /*获取sku的可预定数（共库存）*/
             SELECT
	                    m.uniq_sku,
	                    sum( ii.AVAILABLE_TO_PROMISE_TOTAL ) AS available 
             FROM
	                    romeo.inventory_item ii
	         INNER JOIN 
	                    romeo.inventory_item_detail AS root_iid ON root_iid.inventory_item_id = ii.root_inventory_item_id 
	                    AND root_iid.quantity_on_hand_diff < 0
	         INNER JOIN 
	                    ecshop.ecs_goods_mapping m ON m.product_id = ii.PRODUCT_ID
	         LEFT JOIN 
	                    romeo.dispatch_list dl ON root_iid.ORDER_ID = dl.PURCHASE_ORDER_ID
	         LEFT JOIN 
	                    ecshop.ecs_order_info eoi ON dl.order_id = eoi.order_id
	         LEFT JOIN 
	                    ecshop.forbid_to_reserve_dispatch ftrd ON ftrd.dispatch_list_id = dl.dispatch_list_id 
	                    AND forbid_status = 'N'
	         LEFT JOIN 
	                    ecshop.ecs_order_goods_del eogd ON eogd.rec_id = dl.order_goods_id
	         LEFT JOIN 
	                    ecshop.cancelled_order eco ON eco.order_id = eoi.order_id 
	                    AND eco.cancelled_status = 'C' 
             WHERE
	                    m.uniq_sku IN ('%s') 
	           AND 
	                    ii.facility_id IN (%s) 
	           AND 
	                    ii.AVAILABLE_TO_PROMISE_TOTAL > 0 
	           AND 
	                    ii.QUANTITY_ON_HAND_TOTAL > 0 
	           AND 
	                    ii.STATUS_ID = 'INV_STTS_AVAILABLE' 
	           AND 
	                    ftrd.dispatch_list_id IS NULL 
	           AND (
		                ( dl.dispatch_list_id IS NULL ) 
		            OR /*批量采购*/
		                ( eoi.order_type_id = 'PURCHASE' ) 
		            OR /*批量工单(用采购订单做工单)*/
		            EXISTS (
		                        SELECT
			                            1 
		                        FROM
			                            ecshop.ecs_order_track eot 
		                        WHERE
			                            eot.order_id = eoi.order_id 
		                        AND 
		                                eot.track_status IN ( 'ABNORMAL' )) 
		                            OR /*异常订单对应的工单可以被其他订单预定*/
                                    (
                                        eoi.shipping_time > 0 
                                        AND eoi.shipping_time < UNIX_TIMESTAMP(
                                        DATE_SUB( NOW(), INTERVAL 1 DAY ))
                                    ) 
                                    OR /*1天前已发货订单的工单(包括退货商品)*/
                                    (
                                        eogd.rec_id IS NOT NULL 
                                        AND eogd.delete_time < DATE_SUB( NOW(), INTERVAL 1 DAY )
                                    ) 
		                            OR /*1天前删除的商品对应的工单*/
                                    (
                                        eoi.order_status = 2 
                                        AND (
                                                eco.cancelled_id IS NULL 
                                                OR 
                                                eco.last_update_stamp < DATE_SUB( NOW(), INTERVAL 1 DAY )
                                            )
                                    ) /*1天前已取消订单的工单*/

	                ) 
             GROUP BY
	                    m.uniq_sku
	         HAVING available <= 6;''',
        'getSalesData': '''
             SELECT      
                         eg.uniq_sku,
                         SUM(IF( eoi.order_time >= '%s', eog.goods_number, 0 )) AS day14Sales,
                         SUm(IF( eoi.order_time >= '%s', eog.goods_number, 0 )) AS day28Sales 
             FROM 
                        ecshop.ecs_order_info AS eoi FORCE INDEX ( order_time )
             INNER JOIN 
                        ecshop.ecs_order_goods AS eog ON eog.order_id = eoi.order_id
             INNER JOIN 
                        ecshop.ecs_goods AS eg ON eg.goods_id = eog.goods_id
             WHERE 
                        1
                   AND 
                        eoi.order_type_id = 'SALE'
                   AND 
                        eoi.order_time >= '%s'
                   AND 
                        eg.uniq_sku IN ('%s')
                   AND 
                        eoi.order_status <> '2'
             AND RIGHT
                        (eoi.email, 8) != 'tetx.com'
             AND RIGHT
                        (eoi.email, 8) != 'i9i8.com'
             AND RIGHT
                        (eoi.email, 8) != 'ylan.com'
                   AND 
                        (eoi.order_status != 0 OR
            NOT EXISTS(SELECT 1 FROM ecshop.erp_order_attribute WHERE order_id = eoi.order_id AND attr_name = 'not_cheat'))      
            GROUP BY eg.uniq_sku;''',
        'batchReceiptTotal': '''
             SELECT
                        pt.task_id as '明细id',
                        IFNULL(pf.party_name, eoi.party_id) as '组织名',
                        eoi.pay_id as '支付id',
                        ep.pay_name as '支付方式名',
                        pt.user_name as '导入人',
                        pt.create_time as '导入时间',
                        count( eoi.order_id ) as '订单数量' 
             FROM
                        payment_task pt
             INNER JOIN 
                        payment_task_detail ptd ON pt.task_id = ptd.task_id
             INNER JOIN 
                        ecs_order_info eoi ON eoi.taobao_order_sn = ptd.taobao_order_sn
             INNER JOIN 
                        ecs_payment ep ON eoi.pay_id = ep.pay_id
             LEFT JOIN 
                        romeo.party_facility pf ON pf.party_id = eoi.party_id
             WHERE
                        pt.create_time >= '%s' 
             AND    
                        pt.create_time <= '%s' 
             GROUP BY
                        eoi.party_id, eoi.pay_id, pt.create_time''',

        'batchReceiptDetail': '''
             SELECT
                        pt.task_id as '明细id',
                        IFNULL(pf.party_name, eoi.party_id) as '组织名',
                        eoi.pay_id as '支付id',
                        ep.pay_name as '支付方式名',
                        pt.user_name as '导入人',
                        pt.create_time as '导入时间',
                        ptd.taobao_order_sn as '外部订单号',
                        ptd.received_amount as '收款金额'
             FROM
                        payment_task pt
             INNER JOIN 
                        payment_task_detail ptd ON pt.task_id = ptd.task_id
             INNER JOIN 
                        ecs_order_info eoi ON eoi.taobao_order_sn = ptd.taobao_order_sn
             INNER JOIN 
                        ecs_payment ep ON eoi.pay_id = ep.pay_id
             LEFT JOIN 
                        romeo.party_facility pf ON pf.party_id = eoi.party_id
             WHERE
                        pt.task_id = %s
             GROUP BY 
                        ptd.abs_id   LIMIT 100''',
        '16W-26W': '''
            SELECT      eg.external_cat_id AS cat_id,
                        SUM(IFNULL(eog.goods_number, 0)) AS sale_num
            FROM 
                        ecshop.ecs_order_info AS eoi FORCE INDEX ( order_time )
            INNER JOIN 
                        ecshop.ecs_order_goods AS eog ON eog.order_id = eoi.order_id
            INNER JOIN 
                        ecshop.ecs_goods AS eg ON eg.goods_id = eog.goods_id
            INNER JOIN 
                        ecshop.ecs_goods_attr ega ON eg.goods_id = ega.goods_id and ega.attr_id = '3373'
            WHERE 
                        1
                   AND 
                        eoi.order_type_id = 'SALE'
                   AND 
                        eoi.order_time >= '%s'
                   AND 
                        eoi.order_time <= '%s'
                   AND 
                        ega.attr_value IN ('16W', '18W', '20W', '22W', '24W', '26W')
                   AND 
                        eg.external_cat_id IN (%s)
                   AND 
                        eoi.order_status <> '2'
             AND RIGHT
                        (eoi.email, 8) != 'tetx.com'
             AND RIGHT
                        (eoi.email, 8) != 'i9i8.com'
             AND RIGHT
                        (eoi.email, 8) != 'ylan.com'
                   AND 
                        (eoi.order_status != 0 OR
            NOT EXISTS(SELECT 1 FROM ecshop.erp_order_attribute WHERE order_id = eoi.order_id AND attr_name = 'not_cheat'))''',

        "ALL": '''
                SELECT      eg.external_cat_id AS cat_id,
                            SUM(IFNULL(eog.goods_number, 0)) AS sale_num
                FROM 
                            ecshop.ecs_order_info AS eoi FORCE INDEX ( order_time )
                INNER JOIN 
                            ecshop.ecs_order_goods AS eog ON eog.order_id = eoi.order_id
                INNER JOIN 
                            ecshop.ecs_goods AS eg ON eg.goods_id = eog.goods_id
                WHERE 
                            1
                       AND 
                            eoi.order_type_id = 'SALE'
                       AND 
                            eoi.order_time >= '%s'
                       AND 
                            eoi.order_time <= '%s'
                       AND 
                            eg.external_cat_id IN (%s)
                       AND 
                            eoi.order_status <> '2'
                 AND RIGHT
                            (eoi.email, 8) != 'tetx.com'
                 AND RIGHT
                            (eoi.email, 8) != 'i9i8.com'
                 AND RIGHT
                            (eoi.email, 8) != 'ylan.com'
                       AND 
                            (eoi.order_status != 0 OR
                NOT EXISTS(SELECT 1 FROM ecshop.erp_order_attribute WHERE order_id = eoi.order_id AND attr_name = 'not_cheat'))''',
        "customSize": '''
                SELECT  
                            eg.external_cat_id               AS cat_id,
                            SUM(IFNULL(eog.goods_number, 0)) AS sale_num
                FROM 
                            ecshop.ecs_order_info AS eoi FORCE INDEX ( order_time )
                INNER JOIN 
                            ecshop.ecs_order_goods AS eog ON eog.order_id = eoi.order_id
                INNER JOIN 
                            ecshop.ecs_goods AS eg ON eg.goods_id = eog.goods_id
                INNER JOIN 
                            ecshop.ecs_goods_attr ega ON eg.goods_id = ega.goods_id and ega.attr_id = '3373' # goodsStyle_size
                INNER JOIN 
                            ecshop.ecs_goods_attr ega2 ON eg.goods_id = ega2.goods_id and ega2.attr_id = '3374' #goodsStyle_bust
                WHERE 
                            1
                  AND 
                            eoi.order_type_id = 'SALE'
                  AND 
                            eoi.order_time >= '%s'
                  AND 
                            eoi.order_time <= '%s'
                  AND 
                            eoi.order_status != '2'
                  AND 
                            eg.external_cat_id IN (%s)
                  AND 
                            ega.attr_value = ''
                  AND 
                            ega2.attr_value > ''
                AND RIGHT
                            (eoi.email, 8) != 'tetx.com'
                AND RIGHT
                            (eoi.email, 8) != 'i9i8.com'
                AND RIGHT
                            (eoi.email, 8) != 'ylan.com'
                AND (eoi.order_status != 0 OR
                       NOT EXISTS(SELECT 1 FROM ecshop.erp_order_attribute WHERE order_id = eoi.order_id AND attr_name = 'not_cheat'));''',
        "overSize": '''
                SELECT
                            eg.external_cat_id AS cat_id,
                            eg.external_goods_id,
                            SUM(IFNULL( eog.goods_number, 0 )) AS sale_num 
                FROM
                            ecshop.ecs_order_info AS eoi FORCE INDEX ( order_time )
                INNER JOIN 
                            ecshop.ecs_order_goods AS eog ON eog.order_id = eoi.order_id
                INNER JOIN 
                            ecshop.ecs_goods AS eg ON eg.goods_id = eog.goods_id
                INNER JOIN 
                            ecshop.ecs_goods_attr ega ON eg.goods_id = ega.goods_id
                INNER JOIN 
                            ecshop.ecs_attribute ea ON ega.attr_id = ea.attr_id AND ea.attr_name = 'goodsStyle_size' 
                    WHERE
                            1 
                    AND 
                            eoi.order_type_id = 'SALE' 
                    AND 
                            eoi.order_time >= '%s' 
                    AND 
                            eoi.order_time <= '%s'
                    AND 
                            eg.external_cat_id IN (%s) 
                AND RIGHT 
                            ( eoi.email, 8 ) != 'tetx.com' 
                AND RIGHT 
                            ( eoi.email, 8 ) != 'i9i8.com' 
                AND RIGHT 
                            ( eoi.email, 8 ) != 'ylan.com' 
                    AND 
                            ( eoi.order_status != 0 OR 
                    NOT EXISTS ( SELECT 1 FROM ecshop.erp_order_attribute WHERE order_id = eoi.order_id AND attr_name = 'not_cheat' ) ) 
                GROUP BY
                        eg.external_goods_id'''
    }
    return sql[index]
