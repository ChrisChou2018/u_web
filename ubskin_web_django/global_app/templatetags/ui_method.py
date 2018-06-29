import time

from django import template
from django.conf import settings

from ubskin_web_django.item import models as item_models


register = template.Library()

@register.simple_tag
def build_photo_url(photo_id, pic_version="thumb", pic_type="photos"):
    # identifier = "!"
    if photo_id:
        return "".join([
            settings.MEDIA_URL, pic_type, "/", pic_version,
            "/", photo_id[:2], "/", photo_id, ".jpg"
        ])
    else:
        return "".join(["/static/", "images/", "user-default.jpg"])



@register.simple_tag
def Pagingfunc(current_page, all_count, filter_args, uri=None):
    try:
        current_page = int(current_page)
    except:
        current_page = 1
    data_num = 15
    a, b = divmod(all_count, data_num)
    if b:
        a = a + 1
    show_page = 10
    all_page = a
    uri = uri if uri is not None else '/'
    filter_args = filter_args if filter_args != None else ''
    html_list = []
    half = int((show_page - 1) / 2)
    start = 0
    stop = 0
    if all_page < show_page:
        start = 1
        stop = all_page
    else:
        if current_page < half + 1:
            start = 1
            stop = show_page
        else:
            if current_page >= all_page - half:
                start = all_page - 10
                stop = all_page
            else:
                start = current_page - half
                stop = current_page + half
    if current_page <= 1:
        previous = """
            <li>
            <a href='#' style='cursor:pointer;text-decoration:none;'>
            上一页<span aria-hidden='true'>&laquo;</span>
            </a>
            </li>
        """
    else:
        previous = """
            <li>
            <a href='{0}?page={1}{2}' class='page_btn'  style='cursor:pointer;text-decoration:none;'>
            上一页<span aria-hidden='true'>&laquo;</span>
            </a>
            </li>
        """.format(uri, current_page - 1, filter_args)
    html_list.append(previous)
    for i in range(start, stop + 1):
        if current_page == i:
            temp = """
                <li>
                <a href='{0}?page={1}{2}' class='page_btn' style='background-color:yellowgreen;cursor:pointer;text-decoration:none;'>
                {3}
                </a>
                </li>
            """.format(uri, i, filter_args, i)
        else:
            temp = """
                <li>
                <a href='{0}?page={1}{2}' class='page_btn' style='cursor:pointer;text-decoration:none;'>
                {3}</a>
                </li>
            """.format(uri, i, filter_args, i)
        html_list.append(temp)
    if current_page >= all_page:
        nex = """
            <li>
            <a href='#' style='cursor:pointer;text-decoration:none;'>
            下一页<span aria-hidden='true'>&raquo;</span>
            </a>
            </li>
        """
    else:
        nex = """
            <li>
            <a href='{0}?page={1}{2}' class='page_btn' style='cursor:pointer;text-decoration:none;'>
            下一页<span aria-hidden='true'>&raquo;</span>
            </a>
            </li>
        """.format(uri, current_page + 1, filter_args)
    html_list.append(nex)
    return ''.join(html_list)


@register.simple_tag
def get_value_by_key(a_dict, key):
    return a_dict.get(key)


@register.simple_tag
def get_thumbicon_by_id(item_id):
    item_image_obj = item_models.ItemImages.get_thumbicon_by_item_id(item_id)
    if item_image_obj:
        print(item_image_obj)
        return item_image_obj

@register.simple_tag
def parse_timestamps(timestamps):
    t = time.localtime(timestamps)
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', t)
    return time_str