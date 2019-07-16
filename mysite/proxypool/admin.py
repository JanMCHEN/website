from django.contrib import admin
from .models import ProxyPool
# Register your models here.


class ProxyAdmin(admin.ModelAdmin):
    ordering = ['-score']
    list_display = ['proxy', 'score']


admin.site.register(ProxyPool, ProxyAdmin)
