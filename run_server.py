import os
os.system('uwsgi --socket 127.0.0.1:9001 --file ubskin_web_django/wsgi.py')