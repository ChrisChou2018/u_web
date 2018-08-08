import os
import xlrd

from django.conf import settings

from ubskin_web_django.item import models as item_model


# import item data from weimob xls
def import_item_data(f_path=None):
    # clear old data first
    # item_model.Items.objects.all().delete()
    result_dict = {"result": "error", "message": "未知错误"}
    item_fpath = os.path.join(settings.BASE_DIR, "items.xls") \
        if not f_path else f_path
    book = xlrd.open_workbook(item_fpath)
    
    sh1_key = (
        "id",
        "warehouse",
        "item_code",
        "item_barcode",
        "item_name",
        "capacity",
        # "batch_num",
        # "invalid_date",
        "price",
        "specifications_type_id",
        "categorie_id",
        "origin",
        "brand_id",
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
            if key == 'specifications_type_id':
                if sh1.row(rx)[idx].value:
                    t = dict(item_model.Items.specifications_type_choices)
                    has_flag = False
                    for i in t:
                        if t[i] == sh1.row(rx)[idx].value:
                            has_flag = True
                            obj[key] = i
                    else:
                        if not has_flag:
                            obj[key] = 0
                else:
                    obj[key] = 0
            elif key == 'categorie_id':
                if sh1.row(rx)[idx].value:
                    categories = item_model.Categories
                    v = sh1.row(rx)[idx].value
                    if '_' in v:
                        categorie_type, categorie_name = v.split('_')
                    elif v == '0':
                        categorie_type = '其他'
                        categorie_name = '其他'
                    else:
                        categorie_type = '其他'
                        categorie_name = v
                    if categorie_name and categorie_type:
                        model_obj, has = categories.objects.get_or_create(
                            categorie_type=categorie_type, categorie_name=categorie_name
                        )
                        obj[key] = model_obj.pk
                else:
                    obj[key] = None
            elif key == 'brand_id':
                brand = item_model.Brands
                model_obj, has =  brand.objects.get_or_create(cn_name=sh1.row(rx)[idx].value)
                obj[key] = model_obj.pk
            else:
                obj[key] = sh1.row(rx)[idx].value
        obj.pop('id')
        obj.pop('warehouse')
        # obj.pop('batch_num')
        # obj.pop('invalid_date')
        db_obj = item_model.Items.get_item_obj_by_barcode(obj["item_barcode"])
        if db_obj:
            # print "Updating obj", obj["product_no"], "..."
            db_obj.update(**obj)
        else:
            # print "Inserting obj", obj["product_no"], "..."
            print(obj)
            item_model.Items.create_item(obj)
    
    # rebuild brands
    # item_model.rebuild_item_brands()
    print('success.....')
