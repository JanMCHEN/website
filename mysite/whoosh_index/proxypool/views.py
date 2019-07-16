from django.shortcuts import render
from proxypool.proxy.db import RedisClient
from django.http import JsonResponse
from .models import ProxyPool
from random import sample
# Create your views here.

redis_proxy = RedisClient()


def proxy(request):
    ip_count = redis_proxy.count()
    ip_enable = redis_proxy.count_able()
    return render(request, 'proxy.html', {'ip_count': ip_count, 'ip_enable': ip_enable})


def proxy_get(request):
    proxys = redis_proxy.random()
    return JsonResponse({'proxy': proxys})


def proxy_get_many(request, count=10):
    # 获取多个默认从mysql数据库中拿
    # 只获取100分的代理ip
    pool = ProxyPool.objects.filter(score=100).order_by('-update_time')
    ret = {}
    if len(pool) > count:
        pool = sample(list(pool), count)
    for i, item in enumerate(pool):
        proxys = item.proxy
        ret.setdefault(i, proxys)
    return JsonResponse({'proxy': ret})
