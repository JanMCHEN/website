from django.db import models
# Create your models here.


class ProxyPool(models.Model):
    proxy = models.CharField(max_length=23, default='')
    http = models.BooleanField(verbose_name='是否支持http代理', default=False)
    https = models.BooleanField(verbose_name='是否支持https代理', default=False)
    score = models.SmallIntegerField(verbose_name='分数', default=100)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_exsist = models.BooleanField(default=True, verbose_name='是否存在')

    # def __str__(self):
    #     s = '{}{:>100}'.format(self.proxy, self.score)
    #     return s

    class Meta:
        db_table = 'df_proxy_pool'
        verbose_name = '代理池'
        verbose_name_plural = verbose_name


# class RecordLog(BaseModel):
#     ip = models.ForeignKey(ProxyPool, on_delete=models.CASCADE, verbose_name='访问的哪个代理ip')
#     from_ip = models.CharField(verbose_name='访问者ip', max_length=15)
#
#     class Meta:
#         db_table = 'df_record'
#         verbose_name = '访问日志'
#         verbose_name_plural = verbose_name

