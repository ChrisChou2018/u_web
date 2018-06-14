from my_admin import item_models
from my_admin import member_models


def build_form_data(fields, data):
    return { i:data.get(i) for i in fields }