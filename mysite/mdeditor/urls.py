# coding:utf-8
from django.urls import path
from .views import UploadViewFDFS

urlpatterns = [
    path('uploads/', UploadViewFDFS.as_view(), name='uploads'),
]