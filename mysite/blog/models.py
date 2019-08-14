from django.db import models
from base_model import BaseModel
from uuid import uuid1
from django.conf import settings

# 富文本编辑器
from DjangoUeditor.models import UEditorField
from mdeditor.fields import MDTextField

from django.contrib.auth.models import AbstractUser
from django.contrib import admin
# Create your models here.


class User(AbstractUser, BaseModel):
    '''用户模型类'''
    is_admin = models.BooleanField(default=0, verbose_name="管理员标记")
    head_ico = models.ImageField(verbose_name='头像', upload_to='head_ico', default='', blank=True)
    user_id = models.CharField(verbose_name='用户uuid', default=str(uuid1()).split('-')[3], max_length=10)
    description = models.CharField(verbose_name='用户描述', default='', max_length=500)

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Articles(BaseModel):
    '''用户发表文章模型类'''
    author_name = models.ForeignKey('User', verbose_name='作者', on_delete=models.CASCADE)
    blog_id = models.CharField(verbose_name='文章标识符', default=str(uuid1()).split('-')[0], max_length=15)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    body = MDTextField(blank=False, verbose_name='正文', default='welcome')

    love = models.IntegerField(default=0, verbose_name='点赞人数')
    look_times = models.IntegerField(default=0, verbose_name='浏览次数')
    is_secret = models.BooleanField(default=False, verbose_name='仅自己可见')
    description = models.CharField(verbose_name='文章描述', default='', max_length=50, blank=True)

    class Meta:
        db_table = 'df_articles'
        verbose_name = '博客文章'
        verbose_name_plural = verbose_name


class Comments(BaseModel):
    '''用户评论模型类'''
    commenter = models.ForeignKey('User', verbose_name='评论者', on_delete=models.CASCADE)
    article = models.ForeignKey('Articles', verbose_name='评论文章', on_delete=models.CASCADE)
    # 新加一个字段时注意要有default
    content = MDTextField(blank=False, config_name='less', default='', verbose_name='评论')
    love = models.IntegerField(default=0, verbose_name='赞同人数')

    class Meta:
        db_table = 'df_comments'
        verbose_name = '文章评论'
        verbose_name_plural = verbose_name


class ReplyComment(BaseModel):
    comment = models.ForeignKey(Articles, verbose_name='评论回复', on_delete=models.CASCADE)
    people = models.ForeignKey(User, verbose_name='回复者', on_delete=models.CASCADE)
    content = models.CharField(verbose_name='回复内容', max_length=50)


class LikeCollect(models.Model):
    '''用户点赞收藏判断模型'''
    username = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, verbose_name='文章', on_delete=models.CASCADE)
    liked = models.BooleanField('赞', default=False)
    collected = models.BooleanField('收藏', default=False)

    class Meta:
        db_table = 'df_collect_like'
        verbose_name = '收藏点赞'
        verbose_name_plural = verbose_name


class Share(BaseModel):
    '''分享模型类'''
    auth = models.ForeignKey('User', verbose_name='分享者', on_delete=models.CASCADE)
    description = models.CharField(verbose_name='描述', default='', max_length=200)
    img = models.ImageField(verbose_name='分享图片', upload_to='share_img', default='', blank=True)

    class Meta:
        db_table = 'df_share'
        verbose_name = '分享'
        verbose_name_plural = verbose_name


class Message(models.Model):
    '''用户消息管理模型类'''
    # 注意User.message?.要能获取到内容，要保证两个相关联的字段有不同的关系名
    user = models.ForeignKey('User', verbose_name='用户', on_delete=models.CASCADE, related_name='own_message')
    # null=True表示数据库中该字段可以为空
    from_who = models.ForeignKey('User', verbose_name='来自', on_delete=models.CASCADE,
                                 blank=True, related_name='send_message', null=True)
    content = models.CharField(verbose_name='消息内容', max_length=100)
    send_time = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    has_read = models.BooleanField(default=False, verbose_name='已读')

    class Meta:
        db_table = 'df_message'
        verbose_name = '消息'
        verbose_name_plural = verbose_name
