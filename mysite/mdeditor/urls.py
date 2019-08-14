# coding:utf-8
from django.urls import path
from .views import UploadView

urlpatterns = [
    path('uploads/', UploadView.as_view(), name='uploads'),
]