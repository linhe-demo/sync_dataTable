#! /usr/bin/env python3
import threading

import pymysql
import xlrd


def init():
    return dbConnection()


def Deal(cate, datatype):
    tt = MyThread(cate, datatype)
    tt.start()


def dbConnection():
    return pymysql.connect(host="******", port=123456, database="***", user="***",
                           password="***", connect_timeout=86400)


def sqlmap(index):
    sql = {
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


class MyThread(threading.Thread):
    """
    使用继承的方式实现多线程
    """

    def __init__(self, cate, datatype):
        super().__init__()  # 必须调用父类的构造方法
        self.db = init()
        self.cate = cate
        self.datatype = datatype
        self.beginDate = "2021-01-01 00:00:00"
        self.endDate = "2021-12-31 23:59:59"

    def run(self):
        try:
            cursor = self.db.cursor()
            print("begin category：" + str(self.cate) + "dateType：" + self.datatype)
            sql = sqlmap(self.datatype)
            cursor.execute(sql % (self.beginDate, self.endDate, self.cate))
            results = cursor.fetchall()
            for row in results:
                print("Complete category calculation：" + str(self.cate) + "dateType：" + self.datatype, row)
        except Exception as e:
            raise e


if __name__ == "__main__":
    category = [2, 7, 8, 9, 10, 16, 17, 18, 22]
    for i in category:
        Deal(i, "ALL")  # 品类全部销量
        Deal(i, "16W-26W")  # 16W-26W尺寸 品类销量
        Deal(i, "customSize")  # 自定义尺寸 品类销量
