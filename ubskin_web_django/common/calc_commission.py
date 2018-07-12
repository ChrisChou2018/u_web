# -*- coding: utf-8 -*-

import os
import xlrd
import xlwt
import datetime

from django.conf import settings

import app.models.order_model as order_model
import app.models.discount_model as discount_model


# calc commission from xls
def calc_commission():
    # import commission from discounts
    n_conds = {"status": "normal", "discount_type": "normal"}
    discount_cursor = discount_model.list_discount_by_conds(n_conds)
    normal_discount_dicts = dict()
    for discount in discount_cursor:
        normal_discount_dicts[discount["product_no"]] = {
            "level_1_commission": discount["level_1_commission"],
            "level_2_commission": discount["level_2_commission"]
        }
    
    p_conds = {"status": "normal", "discount_type": "promo"}
    p_discount_cursor = discount_model.list_discount_by_conds(p_conds)
    promo_discount_dicts = dict()
    for discount in p_discount_cursor:
        promo_discount_dicts[discount["product_no"]] = {
            "level_1_commission": discount["level_1_commission"],
            "level_2_commission": discount["level_2_commission"],
            "start_date": discount["start_date"],
            "end_date": discount["end_date"]
        }
    
    # print(promo_discount_dicts["10401001"])
    # return
    
    # print(discount_dicts["0550105"])
    # return

    orders_fpath = os.path.join(settings.BASE_DIR, "orders.xls")
    
    book = xlrd.open_workbook(orders_fpath)
    print("The number of orders is {0}".format(book.nsheets))

    sheet = book.sheet_by_index(0)
    idx = 0

    order_list = list()
    order_dict = dict()
    for rx in range(sheet.nrows):
        if rx == 0:
            continue
        row = sheet.row(rx)
        order_obj = None
        if row[0].value != "":
            if order_dict:
                order_list.append(order_dict)
                # order_obj = order_model.load_order_by_order_id(row[0].value)
                # if order_obj:
                #     print("Updating order", row[0].value, "...")
                    # order_model.update_order_by_order_id(row[0].value, order_dict)
                # else:
                #     print("Inserting order", row[0].value, "...")
                    # order_model.insert_order(order_dict)
            order_dict = {
                "id": row[0].value.strip(),
                # "created_at": row[1].value,
                "type": row[3].value,
                "source": row[4].value,
                "order_status": row[5].value.strip(),
                "payment_status": row[6].value.strip(),
                "delivery_type": row[7].value,
                "logistics_status": row[8].value,
                "balance_paid": row[14].value,
                "should_pay": row[15].value, # 应付货款
                "shipment_fee": row[16].value,
                "total_amount": row[17].value, # 应付金额
                "buyer_paid": row[18].value, # 实际支付金额
                "payment_method": row[19].value,
                "paid_at": row[20].value,
                "buyer_note": row[21].value,
                "seller_note": row[22].value,
                "goods": list()
            }
            raw_data = sheet.cell_value(rowx=rx, colx=1)
            date_obj = datetime.datetime(*xlrd.xldate_as_tuple(raw_data, book.datemode))
            order_dict["created_at"] = int(date_obj.strftime("%Y%m%d"))
            order_obj = order_model.load_order_by_order_id(order_dict["id"])
            if order_obj:
                order_dict["shop_name"] = order_obj["source"]
                order_dict["member_nickname"] = order_obj["member_nickname"]
                order_dict["wechat_nickname"] = order_obj["wechat_nickname"]
                order_dict["member_level"] = order_obj["member_level"]
                order_dict["member_phone"] = order_obj["member_phone"]
            else:
                print("Missing order", order_dict["id"], "...")
        order_dict["goods"].append(
            {
                "name": row[23].value, "id": row[24].value.strip(), "spec": row[25].value,
                "price": row[26].value, "num": row[27].value, "paid": row[28].value,
            }
        )

    
    wbook = xlwt.Workbook()
    wsheet = wbook.add_sheet('Sheet 1')
    style_newline = xlwt.easyxf("align: wrap on")

    wsheet.write(0, 0, u"订单号")
    wsheet.write(0, 1, u"订单详情")
    wsheet.write(0, 2, u"一级返利")
    wsheet.write(0, 3, u"二级返利")
    wsheet.write(0, 4, u"合伙人昵称")
    wsheet.write(0, 5, u"合伙人微信昵称")
    wsheet.write(0, 6, u"合伙人手机号")
    wsheet.write(0, 7, u"订单来源")
    row_index = 1
    for order_obj in order_list:
        order_id = order_obj["id"]
        print("Processing order", order_id, "...")
        if order_obj["order_status"] != u"交易完成" or order_obj["payment_status"] != u"已支付":
            print("Not finished order", order_obj["id"], "...")
            continue
        if order_obj["balance_paid"] == 0:
            continue
        if not "member_nickname" in order_obj:
            continue
        goods_text = ""
        l1_comm_amount = 0
        l2_comm_amount = 0
        no_data_flag = False

        # 根据余额支付的情况, 计算佣金倍率
        bp_rate = 0
        if order_obj["should_pay"] > order_obj["buyer_paid"]:
            # if order_obj["id"] == '6710994922731138894':
            #     print(order_obj["total_amount"], order_obj["buyer_paid"])
            #     print(round((order_obj["total_amount"] - order_obj["buyer_paid"]) / order_obj["total_amount"], 2))
            #     return
            bp_rate = round((order_obj["should_pay"] - order_obj["buyer_paid"]) / order_obj["should_pay"], 2)
        # print(order_obj["total_amount"], order_obj["buyer_paid"])

        for goods in order_obj["goods"]:
            # decide to use normal or promo discount dicts
            discount_dicts = normal_discount_dicts
            if goods["id"] in promo_discount_dicts:
                pdis_obj = promo_discount_dicts[goods["id"]]
                # print(pdis_obj)
                if order_obj["created_at"] >= pdis_obj["start_date"] and \
                        order_obj["created_at"] <= pdis_obj["end_date"]:
                    discount_dicts = promo_discount_dicts
                # if goods["id"] == "10401001":
                #     print(order_obj)
                #     print(order_obj["created_at"], pdis_obj["start_date"], pdis_obj["end_date"])
                #     return

            # if goods["id"] == "0550105":
            #     print(goods["id"], discount_dicts["0550105"])

            if not goods["id"] in discount_dicts:
                goods_text = goods_text + goods["id"] + ", " \
                    + str(goods["price"]) + " x " + str(goods["num"]) + u", 无返利数据\n"
                no_data_flag = True
            else:
                discount_obj = discount_dicts[goods["id"]]
                l1_comm = round(discount_obj["level_1_commission"] * goods["price"] * goods["num"] * bp_rate, 2)
                l2_comm = round(discount_obj["level_2_commission"] * goods["price"] * goods["num"] * bp_rate, 2)
                goods_text = goods_text + goods["id"] + ", " + str(goods["price"]) \
                    + " x " + str(goods["num"]) + u" x " + str(bp_rate) + u"(余额支付比例) "\
                    + u", 一级返利: " + str(l1_comm) + u", 二级返利: " + str(l2_comm) + "\n"
                l1_comm_amount += l1_comm
                l2_comm_amount += l2_comm
            
        wsheet.write(row_index, 0, order_id)
        wsheet.write(row_index, 1, goods_text, style_newline)
        wsheet.write(row_index, 2, str(l1_comm_amount if not no_data_flag else "-"))
        wsheet.write(row_index, 3, str(l2_comm_amount if not no_data_flag else "-"))
        wsheet.write(row_index, 4, order_obj["member_nickname"])
        wsheet.write(row_index, 5, order_obj["wechat_nickname"])
        wsheet.write(row_index, 6, order_obj["member_phone"])
        wsheet.write(row_index, 7, order_obj["shop_name"])
        row_index += 1
    
    wsheet.col(0).width = 256 * 20
    wsheet.col(1).width = 256 * 50
    wsheet.col(4).width = 256 * 15
    wsheet.col(5).width = 256 * 15
    wsheet.col(6).width = 256 * 15
    wsheet.col(7).width = 256 * 40
    comm_path = os.path.join(settings.BASE_DIR, "commissions.xls")
    wbook.save(comm_path)


# ---   ---- #

# import discount data from xls
def import_discount_data():
    discount_file_name = os.path.join(settings.BASE_DIR, "discounts.xls")
    
    book = xlrd.open_workbook(discount_file_name)
    print("The number of worksheets is {0}".format(book.nsheets))
    # print("Worksheet name(s): {0}".format(book.sheet_names())))

    # sheet1: 跨境
    sh1 = book.sheet_by_index(0)
    sh1_keys = (
        # "num",
        # "name",
        # "cost_price",
        # "retail_price",
        # "wholesale_price",
        # "wholesale_discount",
        # "level_1_commission",
        # "level_2_discount",
        # "level_2_commission"

        "line_no",
        "product_no",
        "barcode",
        "name",
        "unit",
        "brand_name",
        "spec",
        "purchase_price",
        "wholesale_price",
        "retail_price",
        "level_1_discount",
        "level_1_commission",
        "level_2_discount",
        "level_2_commission",
    )
    if sh1.ncols != len(sh1_keys):
        print("Sheet 1 wrong format!", sh1.ncols, "exiting...")
        return

    for rx in range(sh1.nrows):
        if rx == 0:
            continue
        if sh1.row(rx)[0].value == u"合计":
            continue
        # print(sh1.row(rx)))
        obj = dict()
        for idx, key in enumerate(sh1_keys):
            obj[key] = sh1.row(rx)[idx].value
        obj["discount_type"] = "normal"

        conds = {"product_no": obj["product_no"], "discount_type": "normal"}
        db_obj = discount_model.load_discount_by_conds(conds)
        if db_obj:
            print("Updating obj", obj["product_no"])
            discount_model.update_discount_by_conds(conds, obj)
        else:
            print("Inserting obj", obj["product_no"])
            discount_model.insert_discount(obj)

    # sheet2: 门店同款
    sh2 = book.sheet_by_index(1)
    sh2_keys = (
        # "num",
        # "name",
        # "cost_price",
        # "retail_price",
        # "wholesale_price",
        # "wholesale_discount",
        # "level_1_commission",
        # "level_2_discount",
        # "level_2_commission",

        "line_no",
        "product_no",
        "barcode",
        "name",
        "unit",
        "brand_name",
        "spec",
        "purchase_price",
        "wholesale_price",
        "retail_price",
        "level_1_discount",
        "level_1_commission",
        "level_2_discount",
        "level_2_commission",
        # "weight",
    )
    print("sh2 cols:", sh2.ncols)
    if sh2.ncols != len(sh2_keys):
        print("Sheet 2 wrong format! exiting...")
        return

    for rx in range(sh2.nrows):
        if rx == 0:
            continue
        obj = dict()
        for idx, key in enumerate(sh2_keys):
            obj[key] = sh2.row(rx)[idx].value
        obj["discount_type"] = "normal"

        conds = {"product_no": obj["product_no"], "discount_type": "normal"}
        db_obj = discount_model.load_discount_by_conds(conds)
        if db_obj:
            print("Updating obj", obj["product_no"])
            discount_model.update_discount_by_conds(conds, obj)
        else:
            print("Inserting obj", obj["product_no"])
            discount_model.insert_discount(obj)

    # sh = book.sheet_by_index(0)
    # print(u"{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols)))
    # print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3))))

    # sheet3: 活动折扣
    sh3 = book.sheet_by_index(2)
    sh3_keys = (
        "line_no",
        "product_no",
        "barcode",
        "name",
        "unit",
        "brand_name",
        "spec",
        "purchase_price",
        "wholesale_price",
        "retail_price",
        "level_1_discount",
        "level_1_commission",
        "level_2_discount",
        "level_2_commission",
        "start_date",
        "end_date",
    )
    print("sh3 cols:", sh3.ncols)
    if sh3.ncols != len(sh3_keys):
        print("Sheet 3 wrong format! exiting...")
        return
    
    # clear old data
    discount_model.remove_many_by_conds({"discount_type": "promo"})
    
    for rx in range(sh3.nrows):
        # skip line_no
        if rx == 0:
            continue
        obj = dict()
        for idx, key in enumerate(sh3_keys):
            if key in ("start_date", "end_date"):
                # convert from date cell
                raw_data = sh3.cell_value(rowx=rx, colx=idx)
                date_obj = datetime.datetime(*xlrd.xldate_as_tuple(raw_data, book.datemode))
                obj[key] = int(date_obj.strftime("%Y%m%d"))
                continue
            obj[key] = sh3.row(rx)[idx].value
        # print(obj["start_date"], obj["end_date"], type(obj["start_date"]))
        # obj["start_date"] = int(obj["start_date"].replace("-", ""))
        # obj["end_date"] = int(obj["end_date"].replace("-", ""))
        obj["discount_type"] = "promo"
        discount_model.insert_discount(obj)
