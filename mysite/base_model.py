from django.db import models

class BaseModel(models.Model):
    '''
    模型类抽象基类
    凡是继承这个类都自带下面三个属性
    '''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_exsist = models.BooleanField(default=True, verbose_name='是否存在')

    class Meta:
        # 说明是一个抽象模型类
        abstract = True
