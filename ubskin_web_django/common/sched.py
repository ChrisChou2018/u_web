import json
import time
import sched
import logging
import requests

WEIXIN_APPID = ''
WEIXIN_APPSECRET = ''

WX_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}"

scheduler = sched.scheduler(time.time, time.sleep)


# update weixin token and js-ticket
def update_weixin_token():
    logging.info("UPDATE_WEIXIN_TOKEN start...")

    # update token
    token_url = WX_TOKEN_URL.format(WEIXIN_APPID, WEIXIN_APPSECRET)
    r_token = requests.get(token_url)
    json_token = json.loads(r_token.text)["access_token"]
    


    scheduler.enter(7000, 1, update_weixin_token, ())
    pass


def start():
    scheduler.enter(5, 1, update_weixin_token, ())

    scheduler.run()
