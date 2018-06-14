**暂时没有写readme.md**

`创建管理员用户`
```
python3 manage.py createsuperuser
```

Development notes
------------
配置文件（涉及到路径、本机配置相关，都在这里设置，不要直接修改 youproject/settings.py）：
请在根目录创建 settings_local.py，内容如下：
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.environ["STATIC_PATH"] = "/path/to/ubskin/static/"
```