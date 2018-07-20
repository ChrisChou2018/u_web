#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

import xlwt
import requests
from django.conf import settings
from bs4 import BeautifulSoup

from ubskin_web_django.member import models as member_model
# import app.models.trader_model as trader_model


def build_cookie_jar(cookie_str):
    jar = requests.cookies.RequestsCookieJar()
    for token in cookie_str.split(";"):
        t_pair = token.strip().split("=")
        jar.set(t_pair[0], t_pair[1])

    return jar


SITE_BASE_URL = "http://www.weimob.com"
OVERWRITE_BASE_URL = "http://fenxiao.weimob.com/index.php"
ORDER_DETAIL_BASE_URL = "http://www.weimob.com"
FX_ORDER_DETAIL_BASE_URL = "http://fenxiao.weimob.com"
ORDER_LIST_BASE_URL = "http://www.weimob.com/vshop/Order/OrderList?PageId=19"


def update_orders(limit_days=30):
    """直接抓取（更新）最近 30 天订单记录"""
    # member_model.OutOrder.objects.all().delete()
    page_num = 1
    while True:
        order_params = {
            "reportrange": "2018/05/01 00:00 - 2018/05/31 23:59",
            "searchBy": 30,
            "pageSize": "100",
            "pageNumber": page_num,
            "orderBy": "desc",
            "order": "Name", 
        }
        cookie_req = build_cookie_jar(AUTH_COOKIE_STR)
        r_order_list = requests.post(ORDER_LIST_BASE_URL, params=order_params, cookies=cookie_req)

        # print r_order_list.status_code, r_order_list.text
        # print(r_order_list.text)

        order_detail_urls = list()
        orders_soup = BeautifulSoup(r_order_list.text, 'lxml')
        for detail_href in orders_soup.find_all("a", {"class": "btn-xs", "title": "查看详情"}):
            order_detail_urls.append(detail_href["href"])
        
        # print order_detail_urls, len(order_detail_urls)
        if not order_detail_urls:
            print("Empty order detail urls, should we return?")
            return
        
        for url in order_detail_urls:
            order_obj = dict()
            r_order = requests.get(SITE_BASE_URL+url, cookies=cookie_req)
            order_soup = BeautifulSoup(r_order.text.encode(r_order.encoding), "lxml")
            # print order_text

            # order status
            order_status_tag = order_soup.find("h5")
            order_obj["order_status"] = str(order_status_tag.text.strip())

            ## order info tag
            order_info_tag = order_soup.find("div", id="tabinfo")

            # order id
            order_id_name_tag = order_info_tag.find("label", text="订单编号")
            if not order_id_name_tag:
                print("Error when fetching order id, exiting...")
                return
            order_id_tag = order_id_name_tag.find_next_sibling("div")
            order_obj["order_id"] = str(order_id_tag.text.strip())
            print("order id:", order_obj["order_id"], "...")

            # order info tags
            order_info_tags = (
                ("source", "订单来源"), ("placed_at", "下单时间")
            )
            for key, text in order_info_tags:
                name_tag = order_info_tag.find("label", text=text)
                if name_tag:
                    info_tag = name_tag.find_next_sibling("div")
                    order_obj[key] = str(info_tag.text).strip()
            # save place date as int
            if "placed_at" in order_obj:
                date_str = order_obj["placed_at"].split(" ")[0]
                order_obj["place_date"] = int(date_str.replace("-", ""))

            # -- order clinet info tag --
            order_client_tag = order_soup.find("div", id="tabspecifications")

            # member level
            member_level_name_tag = order_client_tag.find("label", text="会员等级")
            if not member_level_name_tag:
                print("Error when fetching member level, no level ??? ...")
                return
            member_level_tag = member_level_name_tag.find_next_sibling("div")
            order_obj["member_level"] = str(member_level_tag.text).strip()

            tags = (("wechat_nickname", "粉丝昵称"), ("member_nickname", "会员昵称"), 
                ("member_phone", "手机号码"), ("wechat_id", "wechatID"),
            )
            # wechat nickname
            for key, text in tags:
                name_tag = order_client_tag.find("label", text=text)
                if name_tag:
                    text_tag = name_tag.find_next_sibling("div")
                    order_obj[key] = text_tag.text.strip().encode()
                # print key, order_obj[key]
            
            if order_obj["member_level"] == "线上合伙人":
                print("Found one !!!")
            
            print(order_obj)
            member_model.update_or_create_model_data(
                member_model.OutOrder,
                order_obj
            )
            print("Order", order_obj["order_id"], "saved...")

        page_num += 1


# 导出微客推广订单
def export_weike_orders():
    exp_order_status = ("交易完成", "已发货")
    orders = member_model.OutOrder.list_out_order()
    
    wbook = xlwt.Workbook()
    wsheet = wbook.add_sheet('Sheet 1')
    style_newline = xlwt.easyxf("align: wrap on")

    wsheet.write(0, 0, "订单号")
    wsheet.write(0, 1, "客户昵称")
    wsheet.write(0, 2, "订单来源")
    wsheet.write(0, 3, "客户等级")
    wsheet.write(0, 4, "下单时间")

    wsheet.col(0).width = 256 * 25
    wsheet.col(1).width = 256 * 20
    wsheet.col(2).width = 256 * 50
    wsheet.col(3).width = 256 * 20
    wsheet.col(4).width = 256 * 20
    
    row_index = 1
    for idx, order in enumerate(orders):
        order_id = order["order_id"]
        print("Processing order", order_id, "...")
        row_index = idx + 1
        wsheet.write(row_index, 0, order["order_id"])
        wsheet.write(row_index, 1, order["member_nickname"])
        wsheet.write(row_index, 2, order["source"])
        wsheet.write(row_index, 3, order["member_level"])
        wsheet.write(row_index, 4, order["placed_at"])
    f_path = os.path.join(settings.BASE_DIR, "weike_orders.xls")
    wbook.save(f_path)




# def __old_update_orders():
#     """默认获取（更新）最近 30 天订单记录"""
#     print("Start update orders...")

#     # 1, 获取分销商列表
#     trader_conds = {"status": "normal"}
#     trader_cursor = trader_model.list_traders(trader_conds)
#     traders = [t for t in trader_cursor]

#     # 2, 循环分销商获取其订单
#     if not traders:
#         print("No traders, exiting...")
#         return

#     # 越权
#     for trader in traders:
#         if not all(k in trader for k in ("aid", "fid", "name")):
#             print("Not all key in trader", trader, ", Skipping...")
#             continue
#         overwrite_params = {
#             "c": 'login', "m": "toBeyondLogin",
#             "fid": trader["fid"], "aid": trader["aid"], "aname": trader["name"]
#         }
#         req_cookie_jar = build_cookie_jar(AUTH_COOKIE_STR)
#         print("We are beyond login", trader["fid"], trader["aid"], trader["name"], "...")
#         r_overwrite = requests.get(
#             OVERWRITE_BASE_URL, params=overwrite_params, cookies=req_cookie_jar,
#             allow_redirects=False
#         )
#         t_cookies = r_overwrite.cookies
#         print(t_cookies)
#         # print r_overwrite.text
#         # print r_overwrite.history

#         # 拿到 cookie, 读订单列表
#         req_cookie_jar.set("pc_aid", t_cookies.get("pc_aid"), path="/")
#         req_cookie_jar.set("x_aid", t_cookies.get("x_aid"))
#         # req_cookie_jar.clear(domain="", path="/", name="x_aid")
#         # print t_cookies.get("pc_aid")

#         # fetch all orders from one trader
#         page_num = 1
#         while True:
#             order_params = {
#                 "c": "order", "m": "orderlist",
#                 "pageSize": "100", "pageNumber": page_num, "orderBy": "desc", "order": "Name"
#                 #"reportrange": 
#             }
#             r_orders = requests.post(OVERWRITE_BASE_URL, params=order_params, cookies=req_cookie_jar)
#             print(r_orders.status_code)
#             # print r_orders.text

#             order_detail_urls = list()
#             orders_soup = BeautifulSoup(r_orders.text, 'lxml')
#             # for order_id_span in orders_soup.find_all("span", string=re.compile("订单编号：")):
#             #     print type(order_id_span.text)
#             #     order_ids.append(order_id_span.text.replace(u"订单编号：", ""))

#             for detail_href in orders_soup.find_all("a", {"class": "btn-xs"}):
#                 order_detail_urls.append(detail_href["href"])



#             print(order_detail_urls)
#             # order_model.insert_order_urls(order_detail_urls)

#             if not order_detail_urls:
#                 break

#             for url in order_detail_urls:
#                 order_obj = dict()
#                 r_order = requests.get(
#                     ORDER_DETAIL_BASE_URL+url, headers=COMMON_REQUEST_HEADERS, cookies=req_cookie_jar
#                 )
#                 order_soup = BeautifulSoup(r_order.text.encode(r_order.encoding), "lxml")
#                 # print order_text

#                 # order status
#                 order_status_tag = order_soup.find("h5")
#                 order_obj["status"] = str(order_status_tag.text).strip()

#                 order_info_tag = order_soup.find("div", id="tabinfo")

#                 # order id
#                 order_id_name_tag = order_info_tag.find("label", text="订单编号")
#                 if not order_id_name_tag:
#                     print("Error when fetching order id, exiting...")
#                     return
#                 order_id_tag = order_id_name_tag.find_next_sibling("div")
#                 order_obj["id"] = str(order_id_tag.text).strip()
#                 print("order id:", order_obj["id"], "...")

#                 # order source
#                 order_source_name_tag = order_info_tag.find("label", text="订单来源")
#                 if order_source_name_tag:
#                     order_source_tag = order_source_name_tag.find_next_sibling("div")
#                     order_obj["source"] = str(order_source_tag.text).strip()
                
#                 # order placed time
#                 order_placed_time_name_tag = order_info_tag.find("label", text="下单时间")
#                 if order_placed_time_name_tag:
#                     order_placed_time_tag = order_placed_time_name_tag.find_next_sibling("div")
#                     order_obj["placed_time"] = str(order_placed_time_tag.text).strip()
                
#                 # order paid time
#                 order_paid_time_name_tag = order_info_tag.find("label", text="支付时间")
#                 if order_paid_time_name_tag:
#                     order_paid_time_tag = order_paid_time_name_tag.find_next_sibling("div")
#                     order_obj["paid_time"] = str(order_paid_time_tag.text).strip()
                
#                 # order shipping time
#                 order_shipping_time_name_tag = order_info_tag.find("label", text="发货时间")
#                 if order_shipping_time_name_tag:
#                     order_shipping_time_tag = order_shipping_time_name_tag.find_next_sibling("div")
#                     order_obj["shipping_time"] = str(order_shipping_time_tag.text).strip()

#                 # order auto receive time
#                 order_auto_receive_name_tag = order_info_tag.find("label", text="自动确认收货时间")
#                 if order_auto_receive_name_tag:
#                     order_auto_receive_tag = order_auto_receive_name_tag.find_next_sibling("div")
#                     order_obj["auto_receive_time"] = str(order_auto_receive_tag.text).strip()
                
#                 # order finished time
#                 order_finished_time_name_tag = order_info_tag.find("label", text="完成时间")
#                 if order_finished_time_name_tag:
#                     order_finished_time_tag = order_finished_time_name_tag.find_next_sibling("div")
#                     order_obj["finished_tiem"] = str(order_finished_time_tag.text).strip()
                
#                 # order closed time
#                 order_closed_time_name_tag = order_info_tag.find("label", text="关闭时间")
#                 if order_closed_time_name_tag:
#                     order_closed_time_tag = order_closed_time_name_tag.find_next_sibling("div")
#                     order_obj["closed_time"] = str(order_closed_time_tag.text).strip()
                
                
#                 # order rights close time, skip

#                 order_pay_tag = order_soup.find("div", id="payinfo")

#                 print(order_obj)
#                 return

#             page_num += 1
 
        # for test
        # break


# def _do_update_orders():
#     order_conds = {"status": "new"}
#     order_cursor = order_model.list_orders(order_conds)
#     for order in order_cursor:



AUTH_COOKIE_STR = "x_aid=55967873; __DAYU_PP=zIaZMFfVmBAIBfbimA6A211d9d0ff5e4; rprm_csource=NA; rprm_cuid=MTUxNTEzMjU0ODIy; Hm_lvt_c1df8c79ab44a42f4e36f5ae9b1f6d48=1515132548; weimobSID=enha845j8ah5e1ser701qn80o7; authDataType=weimob; Hm_lvt_d80741dd59de91e1846b2add2c0ad2a2=1515132748; ASP.NET_SessionId=lo0tijp4gbdqw4kumhzfrjl2; pc_aid=pc_55967873; VshopLogin=eyJBSWQiOjU1OTY3ODczLCJQZXJtaXNzaW9ucyI6IiIsIlVzZXJUeXBlIjozLCJDaXBoZXIiOiIyMTEyNDJjOTBmMDVjMzNmZDAyMzhmNmY2NjcxODJlNSIsIkhhc2hVc2VyS2V5IjoiWVRveE16cDdjem8yT2lKMWMyVnlhV1FpTzJrNk5UY3hOekk0T0RJN2N6bzRPaUoxYzJWeWRIbHdaU0k3YVRvek8zTTZPRG9pZFhObGNtNWhiV1VpTzNNNk9Eb2lWVUpUWVdSdGFXNGlPM002TkRvaWJtRnRaU0k3Y3pvNE9pSlZRbE5oWkcxcGJpSTdjem81T2lKclpXVndZV3hwZG1VaU8yazZNRHR6T2pnNkluQmhjM04zYjNKa0lqdHpPak15T2lKaE1HVmlNakkzWlRKbE5HUXlNbVk1Tm1Sak5XSTJaVFU1TVdFNU9URXdaaUk3Y3pveE1qb2libVYzWDNCaGMzTjNiM0prSWp0ek9qTXlPaUl6WVdWbE5qWmpNell4TmpkbFpEWmpZV05tTkdVMk5HWXdaRGcwWmpreU9DSTdjem95TWpvaWFYTmZZMmhoYm1kbFgyNWxkMTl3WVhOemQyOXlaQ0k3Y3pveE9pSXhJanR6T2pFME9pSnBjMTlqYUdGdVoyVmZabXhoWnlJN2N6b3hPaUl4SWp0ek9qRTRPaUpPUlVWRVgxSkZSbEpGVTBoZlRVVk9WVk1pTzA0N2N6b3hNRG9pYzJWeWRtbGpaVjlwWkNJN2N6b3lPaUl4TUNJN2N6bzFPaUpsZEdsdFpTSTdjem94TURvaU1UVXlNalV4TVRrNU9TSTdjem96T2lKbGJuWWlPM002TmpvaVQwNU1TVTVGSWp0OSIsIkpvYk51bWJlciI6IlVCU2FkbWluIiwiSm9iTmFtZSI6IlZVSlRZV1J0YVc0PSIsIlVzZXJJZCI6NTcxNzI4ODIsIlBvd2VySWQiOjB9; express.session=s%3AJg823sFtf9Yn96iOmFpjeHTSBsjqd2ot.eByR6fL1apWfAbl8gE4SvCRpYUBK1gs1VEedvlWu6RM; Hm_lpvt_c1df8c79ab44a42f4e36f5ae9b1f6d48=1516006623; saasAuthData=a36265d25af493a721737192fb6045958e542699646ccd437b7b001b11b40dcb; __hash__=YToxMzp7czo2OiJ1c2VyaWQiO2k6NTcxNzI4ODI7czo4OiJ1c2VydHlwZSI7aTozO3M6ODoidXNlcm5hbWUiO3M6ODoiVUJTYWRtaW4iO3M6NDoibmFtZSI7czo4OiJVQlNhZG1pbiI7czo5OiJrZWVwYWxpdmUiO2k6MDtzOjg6InBhc3N3b3JkIjtzOjMyOiJhMGViMjI3ZTJlNGQyMmY5NmRjNWI2ZTU5MWE5OTEwZiI7czoxMjoibmV3X3Bhc3N3b3JkIjtzOjMyOiIzYWVlNjZjMzYxNjdlZDZjYWNmNGU2NGYwZDg0ZjkyOCI7czoyMjoiaXNfY2hhbmdlX25ld19wYXNzd29yZCI7czoxOiIxIjtzOjE0OiJpc19jaGFuZ2VfZmxhZyI7czoxOiIxIjtzOjE4OiJORUVEX1JFRlJFU0hfTUVOVVMiO047czoxMDoic2VydmljZV9pZCI7czoyOiIxMCI7czo1OiJldGltZSI7czoxMDoiMTUyMjUxMTk5OSI7czozOiJlbnYiO3M6NjoiT05MSU5FIjt9; __verify__=f866ea714494543c97f0156e4eddc092; weimobAuthData=0701f0327e266ad7d30b5d7d78d8e799; __hash__site=YToxMzp7czo2OiJ1c2VyaWQiO2k6NTcxNzI4ODI7czo4OiJ1c2VydHlwZSI7aTozO3M6ODoidXNlcm5hbWUiO3M6ODoiVUJTYWRtaW4iO3M6NDoibmFtZSI7czo4OiJVQlNhZG1pbiI7czo5OiJrZWVwYWxpdmUiO2k6MDtzOjg6InBhc3N3b3JkIjtzOjMyOiJhMGViMjI3ZTJlNGQyMmY5NmRjNWI2ZTU5MWE5OTEwZiI7czoxMjoibmV3X3Bhc3N3b3JkIjtzOjMyOiIzYWVlNjZjMzYxNjdlZDZjYWNmNGU2NGYwZDg0ZjkyOCI7czoyMjoiaXNfY2hhbmdlX25ld19wYXNzd29yZCI7czoxOiIxIjtzOjE0OiJpc19jaGFuZ2VfZmxhZyI7czoxOiIxIjtzOjE4OiJORUVEX1JFRlJFU0hfTUVOVVMiO047czoxMDoic2VydmljZV9pZCI7czoyOiIxMCI7czo1OiJldGltZSI7czoxMDoiMTUyMjUxMTk5OSI7czozOiJlbnYiO3M6NjoiT05MSU5FIjt9; wsession_id=enha845j8ah5e1ser701qn80o7; Hm_lpvt_d80741dd59de91e1846b2add2c0ad2a2=1516006626; ci_session=a%3A5%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22d93e545aa70f1223661ee9f6bf15995c%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A11%3A%2210.16.80.52%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A120%3A%22Mozilla%2F5.0+%28Macintosh%3B+Intel+Mac+OS+X+10_13_2%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F63.0.3239.132+Safari%2F537.3%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1516014465%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7Dd48a70baac03432a6e46151b72f3df377ed5ddcc"

COMMON_REQUEST_HEADERS = {
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
}
