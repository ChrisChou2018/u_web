import os
import xlrd

from django.conf import settings

# import app.models.item_model as item_model
from ubskin_web_django.item import models as item_model


# import item data from weimob xls
def import_item_data(f_path=None):
    # clear old data first
    item_model.Items.objects.all().delete()
    result_dict = {"result": "error", "message": "未知错误"}
    item_fpath = os.path.join(settings.BASE_DIR, "items.xls") \
        if not f_path else f_path
    book = xlrd.open_workbook(item_fpath)
    
    sh1_key = (
        "id",
        "item_code",
        "item_barcode",
        "item_name",
        "specifications_type",
        "brand_name",
        "capacity",
        "original_price",
        "current_price",
        "price"
        # "brand_name", "product_no", "name", "barcode", "type_name"
    )

    sh1 = book.sheet_by_index(0)
    if sh1.ncols != len(sh1_key):
        print(sh1.ncols, len(sh1_key))
        print("Sheet 1 wrong format!(", sh1.ncols, ") exiting...")
        result_dict["message"] = "要导入的文件格式不正确"
        return result_dict

    for rx in range(sh1.nrows):
        if rx == 0:
            continue
        # if sh1.row(rx)[0].value == u""
        # print sh1.row(rx)
        obj = dict()
        for idx, key in enumerate(sh1_key):
            obj[key] = sh1.row(rx)[idx].value
        obj.pop('id')
        db_obj = item_model.Items.get_item_obj_by_barcode(obj["item_barcode"])
        if db_obj:
            # print "Updating obj", obj["product_no"], "..."
            db_obj.update(**obj)
        else:
            # print "Inserting obj", obj["product_no"], "..."
            item_model.Items.create_item(obj)
    
    # rebuild brands
    # item_model.rebuild_item_brands()
    print('success.....')
