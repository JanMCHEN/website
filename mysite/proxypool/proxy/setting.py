# Redis数据库地址
REDIS_HOST = '139.224.13.150'

# Redis端口
REDIS_PORT = 6379

# Redis密码，如无填None
REDIS_PASSWORD = 'Cjm0719@'

REDIS_KEY = 'proxies'

# 代理分数
MAX_SCORE = 100
MIN_SCORE = 50
INITIAL_SCORE = 60

VALID_STATUS_CODES = [200, 302]

# 代理池数量界限
POOL_UPPER_THRESHOLD = 5000

# 检查周期
TESTER_CYCLE = 60
# 获取周期
GETTER_CYCLE = 600

# 测试API，建议抓哪个网站测哪个
TEST_URL = ('https://www.baidu.com', )

# # API配置
# API_HOST = '0.0.0.0'
# API_PORT = 5555

# 开关
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = False
SYNC_ENABLED = True

# 最大批测试量
BATCH_TEST_SIZE = 10




# django配置
import os
SECRET_KEY = 'b$jh)pp9_iirzd3s-lga*i0mt$o^%jfj9#$ch3fnhxqe2m_l8#'

# Application definition

INSTALLED_APPS = [
    'proxypool',
]


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': 'Cjm0719@',
        'HOST': '139.224.13.150',
        'PORT': '3306',
    }
}
