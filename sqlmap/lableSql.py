def sqlmap(index):
    sql = {
        "JJSLightDressBaseData": '''
                SELECT
                        egm.p_sku AS PSKU,
                        egm.uniq_sku,
                        egm.p_id AS PID,
                        eg.external_goods_id AS GID,
                        ega1.attr_value AS 颜色,
                        ega2.attr_value AS 尺码,
                        DATE_FORMAT( jgosr.on_sale_time, '%s' ) AS id首次上架时间,
                        ( SELECT max( jgosr3.on_sale_time ) FROM ecshop.jjs_goods_on_sale_record jgosr3 WHERE jgosr3.external_goods_id = jgosr.external_goods_id AND jgosr3.type = '1' ) AS id最近一次上架时间,
                        (
                        SELECT
                            SUM( eog2.goods_number ) 
                        FROM
                            ecshop.ecs_goods_mapping egm2
                            INNER JOIN ecshop.ecs_goods eg2 ON eg2.uniq_sku = egm2.uniq_sku
                            INNER JOIN ecshop.ecs_order_goods eog2 ON eg2.goods_id = eog2.goods_id
                            INNER JOIN ecshop.ecs_order_info eoi3 ON eoi3.order_id = eog2.order_id 
                        WHERE
                            egm2.p_sku = egm.p_sku 
                            AND eoi3.order_time >= jgosr.on_sale_time 
                            AND RIGHT ( eoi3.email, 8 ) NOT IN ( 'tetx.com', 'ylan.com', 'i9i8.com' ) 
                            AND eoi3.order_type_id = 'SALE' 
                            AND eoi3.order_status != '2' 
                        ) AS PSKU上架以来总销量 
                FROM
                            ecshop.jjs_goods_on_sale_record jgosr
                INNER JOIN 
                            ecshop.ecs_goods eg ON jgosr.external_goods_id = eg.external_goods_id
                INNER JOIN 
                            ecshop.ecs_goods_mapping egm ON eg.uniq_sku = egm.uniq_sku
                INNER JOIN 
                            ecshop.ecs_goods_label egl ON egm.p_id = egl.pid AND egl.type = 10 AND egl.label = 10307
                LEFT JOIN 
                            ecshop.ecs_goods_attr ega1 ON ega1.goods_id = eg.goods_id AND ega1.attr_id = '3367' -- goodsStyle_color
                LEFT JOIN 
                            ecshop.ecs_goods_attr ega2 ON ega2.goods_id = eg.goods_id AND ega2.attr_id = '3373' -- goodsStyle_size
                LEFT JOIN 
                            ecshop.editor_goods eg1 ON jgosr.external_goods_id = eg1.goods_id 
                WHERE
                            eg.external_cat_id = '%s' 
                AND 
                            eg.goods_party_id = '%s'
                AND 
                            jgosr.type = 1 
                AND 
                            jgosr.id = ( SELECT min( jgosr2.id ) FROM ecshop.jjs_goods_on_sale_record jgosr2 WHERE jgosr2.external_goods_id = jgosr.external_goods_id AND jgosr2.type = '1' );
        ''',
        "JJSLightDressReceiptData": '''
                SELECT
                        egm.p_sku AS PSKU,
                        sum( iid.QUANTITY_ON_HAND_DIFF ) AS 入库数
                FROM
                        romeo.inventory_item_detail AS iid
                        INNER JOIN romeo.inventory_item AS ii ON ii.INVENTORY_ITEM_ID = iid.INVENTORY_ITEM_ID
                        INNER JOIN romeo.inventory_item_detail AS root_iid ON root_iid.INVENTORY_ITEM_ID = ii.ROOT_INVENTORY_ITEM_ID 
                        AND root_iid.QUANTITY_ON_HAND_DIFF < 0
                        INNER JOIN ecshop.ecs_order_info AS eoi ON eoi.order_id = iid.ORDER_ID
                        INNER JOIN ecshop.ecs_goods AS eg ON eg.product_id = ii.PRODUCT_ID
                        INNER JOIN ecshop.ecs_goods_mapping egm ON eg.uniq_sku = egm.uniq_sku 
                WHERE
                        egm.p_sku IN ('%s') 
                        AND iid.QUANTITY_ON_HAND_DIFF > 0 
                        AND eoi.order_type_id IN ( 'SALE', 'PURCHASE' ) 
                        AND ii.FACILITY_ID IN ( '30246773', '369258324' ) 
                        AND ii.STATUS_ID = 'INV_STTS_AVAILABLE' 
                GROUP BY
                        egm.p_sku;
        ''',
        "JJSLightDressAvailableData": '''
                SELECT
                            egm.p_sku AS PSKU,
                            sum( is2.AVAILABLE_TO_RESERVED ) AS 可预定量 
                FROM
                            ecshop.ecs_goods_mapping egm
                INNER JOIN 
                            romeo.inventory_summary is2 ON egm.product_id = is2.PRODUCT_ID AND is2.FACILITY_ID IN ('30246773', '369258324') AND is2.STATUS_ID = 'INV_STTS_AVAILABLE' 
                WHERE
                            egm.p_sku IN ('%s') 
                GROUP BY
                            egm.p_sku
        ''',
        "JJSLightDressStockData": '''
                SELECT
                            egm.p_sku AS PSKU,
                            spd.suggest_quantity AS 备货数 
                FROM
                            ecshop.ecs_goods_mapping egm
                INNER JOIN 
                            ecshop.stock_plan_detail spd ON egm.uniq_sku = spd.uniq_sku and spd.status = 1
                WHERE
                            egm.p_sku = '%s'
                ORDER BY
                            spd.id ASC 
                LIMIT       3
        ''',
        "JJSLightDressReceiptThreeTimesData": '''
                SELECT
                            egm.p_sku AS PSKU,
                            sum( iid.QUANTITY_ON_HAND_DIFF ) AS 入库数,
                            FROM_UNIXTIME( UNIX_TIMESTAMP( iid.CREATED_STAMP ), '%s' ) AS tmpDate 
                FROM
                            romeo.inventory_item_detail AS iid
                INNER JOIN 
                            romeo.inventory_item AS ii ON ii.INVENTORY_ITEM_ID = iid.INVENTORY_ITEM_ID
                INNER JOIN 
                            romeo.inventory_item_detail AS root_iid ON root_iid.INVENTORY_ITEM_ID = ii.ROOT_INVENTORY_ITEM_ID 
                            AND root_iid.QUANTITY_ON_HAND_DIFF < 0
                INNER JOIN 
                            ecshop.ecs_order_info AS eoi ON eoi.order_id = iid.ORDER_ID
                INNER JOIN 
                            ecshop.ecs_goods AS eg ON eg.product_id = ii.PRODUCT_ID
                INNER JOIN 
                            ecshop.ecs_goods_mapping egm ON eg.uniq_sku = egm.uniq_sku 
                WHERE
                            egm.p_sku = '%s' 
                AND     
                            iid.QUANTITY_ON_HAND_DIFF > 0 
                AND 
                            eoi.order_type_id IN ( 'SALE', 'PURCHASE' ) 
                AND 
                            ii.FACILITY_ID IN ( '30246773', '369258324' ) 
                AND 
                            ii.STATUS_ID = 'INV_STTS_AVAILABLE' 
                GROUP BY
                            tmpDate 
                ORDER BY
                            tmpDate ASC 
                LIMIT 3
                                '''
    }
    return sql[index]
