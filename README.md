**暂时没有写readme.md**

`创建管理员用户`
```
python3 manage.py createsuperuser
```

Development notes
------------
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