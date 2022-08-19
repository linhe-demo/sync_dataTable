def sqlmap(index):
    sql = {
        'getCategorySku': ''' /*获取品类下的sku,gid,pid信息*/
             SELECT 
                        eg.external_goods_id, ega.attr_value AS color, egm.p_id, pgm.master_goods_id
             FROM 
                        ecshop.ecs_goods eg 
             INNER JOIN
	                    ecshop.ecs_goods_attr ega ON ega.goods_id = eg.goods_id AND ega.attr_id = '3367' -- goodsStyle_color
	         INNER JOIN 
	                    ecshop.ecs_goods_mapping egm ON eg.uniq_sku = egm.uniq_sku
	         INNER JOIN
	                    ecshop.pms_goods_mapping pgm ON eg.external_goods_id = pgm.external_goods_id
             WHERE
                        eg.goods_party_id = %s 
             AND 
                        eg.external_cat_id = %s''',
        'co-inventory': '''
             SELECT
                        pms2.external_goods_id
			 FROM
			            ecshop.pms_goods_mapping pms1
			 INNER JOIN
			            ecshop.pms_goods_mapping pms2 ON pms2.master_goods_id = pms1.master_goods_id
			 WHERE
			            pms1.external_goods_id in ('%s')
			 UNION
			 
			 SELECT 
			            goods_id as external_goods_id
			 FROM 
			            ecshop.editor_goods
			 WHERE 
			            goods_id in ('%s')
        ''',
        'getInventoryNumber': ''' /*获取pskc的可预定数（共库存, 国内可预订量，国外可预订量）*/
             SELECT
	                    CONCAT( IFNULL( pms.p_id, eg.external_goods_id ), ega1.attr_value) skey,
	                    SUM(IF( `is`.facility_id IN ( '30246773', '369258324' ), `is`.available_to_reserved, 0 )) AS num,
	                    SUM(IF( `is`.facility_id NOT IN ( '30246773', '369258324', '762503641' ), `is`.available_to_reserved, 0 )) AS numOverseas 
             FROM
	                    romeo.inventory_summary AS `is`
	         INNER JOIN 
	                    ecshop.ecs_goods AS eg ON eg.product_id = `is`.product_id
	         LEFT JOIN 
	                    ecshop.pms_goods_mapping pms ON pms.external_goods_id = eg.external_goods_id
	         INNER JOIN 
	                    ecshop.ecs_goods_attr ega1 ON ega1.goods_id = eg.goods_id 
	                    AND ega1.attr_id = 3367
             WHERE
                        `is`.status_id = 'INV_STTS_AVAILABLE' 
             AND
                        `is`.available_to_reserved > 0 
             AND
                        eg.external_goods_id IN ('%s') 
             GROUP BY
	                    skey;''',
        'getSalesData': ''' /* 销量数据 (共库存)*/
             SELECT
	                    CONCAT( IFNULL( pms.p_id, eg.external_goods_id ), ega1.attr_value ) skey,
	                    SUM(IF( eoi.order_time >= '%s', eog.goods_number, 0 )) AS day14Sales,
	                    SUM(IF( eoi.order_time >= '%s', eog.goods_number, 0 )) AS day28Sales 
             FROM
	                    ecshop.ecs_order_info AS eoi FORCE INDEX ( order_time )
	         INNER JOIN 
	                    ecshop.ecs_order_goods AS eog ON eog.order_id = eoi.order_id
	         INNER JOIN 
	                    ecshop.ecs_goods AS eg ON eg.goods_id = eog.goods_id
	         LEFT JOIN 
	                    ecshop.pms_goods_mapping pms ON pms.external_goods_id = eg.external_goods_id
	         INNER JOIN 
	                    ecshop.ecs_goods_attr ega1 ON ega1.goods_id = eg.goods_id 
	                    AND ega1.attr_id = 3367
	         LEFT JOIN 
	                    romeo.order_inv_reserved_detail AS oird ON oird.order_item_id = CONVERT ( eog.rec_id USING utf8 ) 
	                    AND oird.STATUS = 'N' 
             WHERE
                        eoi.party_id IN (%s) 
	         AND 
	                    eoi.order_type_id = 'SALE' 
	         AND 
	                    eoi.order_time >= '%s' 
	         AND RIGHT ( eoi.email, 8 ) != 'tetx.com' 
	         AND RIGHT ( eoi.email, 8 ) != 'i9i8.com' 
	         AND RIGHT ( eoi.email, 8 ) != 'ylan.com' 
	         AND eg.external_goods_id IN ('%s') 
             GROUP BY
	                    skey''',
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
