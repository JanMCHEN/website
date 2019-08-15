# coding:utf-8
import json
from django.views import generic
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .configs import MDConfig
from fdfs_client.client import Fdfs_client, get_tracker_conf

# TODO 此处获取default配置，当用户设置了其他配置时，此处无效，需要进一步完善
MDEDITOR_CONFIGS = MDConfig()


class UploadViewFDFS(generic.View):
    option = settings.CUSTOM_STORAGE_OPTIONS

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadViewFDFS, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)

        # image none check
        if not upload_image:
            return HttpResponse(json.dumps({
                'success': 0,
                'message': "未获取到要上传的图片",
                'url': ""
            }))

        # image format check
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return HttpResponse(json.dumps({
                'success': 0,
                'message': "上传图片格式错误，允许上传图片格式为：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
                'url': ""
            }))

        # FDFS 存储文件
        client_conf_obj = get_tracker_conf(self.option.get('CLIENT_CONF'))
        client = Fdfs_client(client_conf_obj)
        ret = client.upload_by_buffer(upload_image.read())
        if ret.get("Status") != "Upload successed.":
            return HttpResponse(json.dumps({
                'success': 0,
                'message': "上传失败：%s" % str(ret.get("Status")),
                'url': ""
            }))

        file_name = ret.get("Remote file_id").decode()

        return HttpResponse(json.dumps({'success': 1,
                                        'message': "上传成功！",
                                        'url': self.option.get('BASE_URL') + file_name}))
