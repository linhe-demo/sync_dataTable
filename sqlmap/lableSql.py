def sqlmap(index):
    sql = {
        "JJSLightDressBaseData": '''
                SELECT
                        egm.p_sku AS PSKU,
                        egm.p_id AS PID,
                        eg.external_goods_id AS GID,
                        ega1.attr_value AS 颜色,
                        ega2.attr_value AS 尺码,
                        DATE_FORMAT( eg1.on_sale_time, '%s' ) AS id最近一次上架时间,
                        jgosr.on_sale_time AS id首次上架时间,
                        (
                        SELECT
                            SUM( eog2.goods_number ) 
                        FROM
                            ecshop.ecs_goods eg2
                            INNER JOIN ecshop.ecs_order_goods eog2 ON eg2.goods_id = eog2.goods_id
                            INNER JOIN ecshop.ecs_order_info eoi3 ON eoi3.order_id = eog2.order_id 
                        WHERE
                            eg2.uniq_sku = eg.uniq_sku 
                            AND RIGHT ( eoi3.email, 8 ) != 'tetx.com' 
                            AND RIGHT ( eoi3.email, 8 ) != 'i9i8.com' 
                            AND RIGHT ( eoi3.email, 8 ) != 'ylan.com' 
                            AND eoi3.order_type_id = 'SALE' 
                        ) AS PSKU上架以来总销量
                FROM
                        ecshop.ecs_goods eg
                        INNER JOIN ecshop.ecs_goods_mapping egm ON eg.uniq_sku = egm.uniq_sku
                        INNER JOIN ecshop.ecs_goods_label egl ON egm.p_id = egl.pid 
                        AND type = 10 
                        AND label = 10307
                        LEFT JOIN ecshop.ecs_goods_attr ega1 ON ega1.goods_id = eg.goods_id 
                        AND ega1.attr_id = '3367' -- goodsStyle_color
                        LEFT JOIN ecshop.ecs_goods_attr ega2 ON ega2.goods_id = eg.goods_id 
                        AND ega2.attr_id = '3373' -- goodsStyle_size
                        LEFT JOIN ecshop.editor_goods eg1 ON eg.external_goods_id = eg1.goods_id
                        LEFT JOIN ecshop.jjs_goods_on_sale_record jgosr ON jgosr.external_goods_id = eg.external_goods_id 
                        AND jgosr.type = 1 
                WHERE
                        eg.external_cat_id = '%s'
                AND 
                        eg.goods_party_id = '%s'
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
