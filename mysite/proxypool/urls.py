from django.urls import path
from . import views

app_name = 'proxy'
urlpatterns = [
    path('get/', views.proxy_get, name='proxy_get'),
    path('get_many/<int:count>',views.proxy_get_many, name='proxy_get_many'),
    path('', views.proxy, name='proxy'),
    ]
