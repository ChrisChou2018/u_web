import requests

def request_user_session_key(js_code):
    appid = 'wx0c02c3d4a853be8d'
    app_secret = 'abffc0cf93f41a4d2565d0c2f3bf164d'
    __url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}& \
                grant_type=authorization_code'.format(appid, app_secret, js_code)
    response = requests.get(__url).content
    data = response.decode()
    return data
