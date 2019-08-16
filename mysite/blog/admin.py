from django.contrib import admin
from .models import User, Articles, Comments, Share, Message
# Register your models here.


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'title']


class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_who', 'content']


class CommentsAdmin(admin.ModelAdmin):
    list_display = ['commenter', 'article']


admin.site.register(User)
admin.site.register(Articles, ArticlesAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Share)
admin.site.register(Message, MessageAdmin)
