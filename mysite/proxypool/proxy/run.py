import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import io
import django
import pymysql
pymysql.install_as_MySQLdb()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setting')
django.setup()
from scheduler import Scheduler
# 解决print编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    try:
        s = Scheduler()
        s.run()
    except:
        main()


if __name__ == '__main__':
    # 每次重新启动都清理一遍代理池
    # redis = RedisClient()
    # redis.clear()
    main()


