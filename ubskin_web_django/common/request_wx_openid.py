import json

import requests

def request_user_session_key(appid, js_code, secret):
    __url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}& \
                grant_type=authorization_code'.format(appid, secret, js_code)
    response = requests.get(__url).content
    data = response.decode()
    data = json.loads(data)
    return data

r""" 返回参数
return_value{
        "session_key":"LyJOfrPds9f\/bp11QjEDcA==",
        "openid":"oJALH5QWt_PWW5W5LZPYCzGSrQfI"
}
"""