初始化
============

`创建管理员用户`
```
python3 manage.py createsuperuser
```

`数据库初始化`
```
python3 run_migrate.py
```

`初始化数据`
```
#执行命令类的

#倒入商品
python manage.py import_item
# 倒入外部订单数据表
python manage.py update_out_order

#请求url快捷倒入数据类的


#快速导入收货方地址URL
/create_recv
#快速导入品牌
/create_brand

```


配置文件相关
==========
配置文件（本机配置相关，都在这里设置，不要直接修改 youproject/settings.py）：
请在根目录创建 settings_local.py，内容如下：
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_NAME"] = "ubskin_web"
os.environ["DB_PORT"] = "3306"
```

服务器配置文件
------------
推荐使用 Nginx + uWsgi 作为本地 Web 服务器,服务器采用动静分离设计，nginx处理所有静态文件，uWsgi处理动态请求

复制 conf/vhost_dev.conf 为 conf/vhost_dev_xxx.conf，xxx 建议为用户名。

`注意修改nginx配置文件中的静态文件地址`
```
location /static/ {
    alias /Users/ChrisChou/Public/my_documents/ubskin_web_django/ubskin_web_django/static/;
  }

location /media/ {
    alias /users/chrischou/public/my_documents/media/;
}

```
`修改uwsgi配置文件中的`
```
chdir=/Users/ChrisChou/public/my_documents/ubskin_web_django # 项目根目录
pidfile=/Users/ChrisChou/Public/my_documents/ubskin_web_django/conf/script/uwsgi.pid # 你的uwsgi运行之后生成的pid文件路径

```

然后在 Nginx 配置文件中导入该文件即可：
```
include /Users/matt/Projects/ubskin_web/conf/vhost_dev.conf;
```

项目启动说明
确认nginx配置文件没有问题后启动nginx
`动态路由交给uwsgi`
执行
```
uwsgi --socket 127.0.0.1:9001 --file ubskin_web_django/wsgi.py  # 具体IP和端口需要和nginx配置文件上保持一致
```


`运行自动化任务`
执行到期自动确认收货订单
```
python manage.py crontab add #将生成任务ID之后执行
python manage.py crontab run ebb2a9c313b47207ced3f1c7ab8b4c47 #run后面跟随任务ID
python manage.py crontab remove #清除所有的计划任务
```


`将数据库数据导出保存为json数据`
执行命令
```
# 导出 item app下的models中所有的数据
python manage.py dumpdata --format=json item > ubskin_web_django/item/fixtures/item_initial_data.json
# 导入item app 数据
python manage.py loaddata item_initial_data.json

# 导出 member app下的models中所有的数据
python manage.py dumpdata --format=json member > ubskin_web_django/member/fixtures/member_initial_data.json
# 导入member app 数据
python manage.py loaddata member_initial_data.json

# 导出 order app下的models中所有的数据
python manage.py dumpdata --format=json order > ubskin_web_django/order/fixtures/order_initial_data.json
# 导入order app 数据
python manage.py loaddata order_initial_data.json


# 将数据库清空的命令
python manage.py flush

```


