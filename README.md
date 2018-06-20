初始化
============

`创建管理员用户`
```
python3 manage.py createsuperuser
```

`数据库初始化`
```
python3 manage.py makemigrations
python3 manage.py migrate
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