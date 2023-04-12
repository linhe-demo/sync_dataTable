def sqlmap(index):
    sql = {
        "getWarehouseCodeBySku": '''
            SELECT warehouse_code FROM ff_wms.fw_goods_shipping_detail WHERE sku in ('%s') and shipment_sn = '%s'
            ''',
        "getInventoryInfo": '''
            select 
                    sku, available_qty, location_code
            FROM
                    ff_wms.fw_inventory 
            WHERE 
                    warehouse_code = '%s' 
            AND 
                    sku IN ('%s') 
            AND 
                    quality in (100) and `status` in (500) group by sku;
        ''',
        "getShippingInfo": '''
            select 
                        fgsd.sku, fgsd.plan_quantity
            from 
                        ff_wms.fw_goods_shipping fgs 
            INNER JOIN 
                        ff_wms.fw_goods_shipping_detail fgsd ON fgs.shipment_sn = fgsd.shipment_sn and fgs.warehouse_code = fgsd.warehouse_code
            where 
                        fgs.warehouse_code = '%s'
            and 
                        fgs.order_status in (10,11,13,14)
            and         
                        fgsd.sku in ('%s')
        '''
    }
    return sql[index]
