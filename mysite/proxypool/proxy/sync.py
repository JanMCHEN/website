from db import RedisClient
from proxypool.models import ProxyPool
from setting import REDIS_KEY


class Sync(object):
    """
    mysql与redis数据同步
    """
    def __init__(self):
        self.redis = RedisClient()
        self.pool = ProxyPool.objects.filter(is_exsist=True)
        # ProxyPool.objects.filter(proxy='').delete()

    def sync_start(self):
        # mysql同步到redis
        for item in self.pool:
            proxy = item.proxy
            score = item.score
            self.redis.add(proxy, score, mysql_save=False)
        # redis同步到mysql
        for proxy in self.redis.all():
            self.redis.mysql_add(proxy)


