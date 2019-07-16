import redis
import re, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from error import PoolEmptyError
from setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY
from setting import MAX_SCORE, MIN_SCORE, INITIAL_SCORE
from proxypool.models import ProxyPool
from random import choice


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    def mysql_add(self, proxy, score=10, http=None):
        obj, created = ProxyPool.objects.get_or_create(proxy=proxy)
        obj.score = score
        if http == 'http':
            obj.http = True
        elif http == 'https':
            obj.https = True
        else:
            obj.https = obj.http = False
        obj.save()

    def mysql_delete(self, proxy):
        ProxyPool.objects.filter(proxy=proxy).update(is_exsist=False)
    
    def add(self, proxy, score=INITIAL_SCORE, mysql_save=True):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        if not self.db.zscore(REDIS_KEY, proxy):
            # 默认存到mysql数据库
            if mysql_save:
                self.mysql_add(proxy, score)
            return self.db.zadd(REDIS_KEY, {proxy: score})
    
    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError
    
    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            self.mysql_add(proxy, score-1)
            return self.db.zincrby(REDIS_KEY, -1, proxy)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            self.mysql_delete(proxy)
            return self.db.zrem(REDIS_KEY, proxy)
    
    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) == None
    
    def max(self, proxy, http=None):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        self.mysql_add(proxy, MAX_SCORE, http)
        return self.db.zadd(REDIS_KEY, {proxy: MAX_SCORE})
    
    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)

    def count_able(self):
        """
        获取有效数量
        :return: 数量
        """
        return len(self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE))

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
    
    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop - 1)

    def clear(self):
        self.db.delete(REDIS_KEY)


if __name__ == '__main__':
    conn = RedisClient()
    result = conn.batch(680, 688)
    print(result)
