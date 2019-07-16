from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client, get_tracker_conf
from django.utils.deconstruct import deconstructible


# 存储类必须是：ref：deconstructible，以便在迁移中的字段上使用它时可以序列化。 只要你的字段有自己的参数：ref：serializable，
# 你可以使用django.utils.deconstruct.deconstructible类装饰器（这是Django在FileSystemStorage上使用的）
@deconstructible
class FdfsStorage(Storage):
    def __init__(self, option=None):
        if not option:
            self.option = settings.CUSTOM_STORAGE_OPTIONS
        else:
            self.option = option

    def _open(self, name, mode='rb'):
        """
        用不到打开文件，所以省略
        """
        pass

    def _save(self, name, content):
        """
        在FastDFS中保存文件
        :param name: 传入的文件名
        :param content: 文件内容
        :return: 保存到数据库中的FastDFS的文件名
        """
        client_conf_obj = get_tracker_conf(self.option.get('CLIENT_CONF'))
        client = Fdfs_client(client_conf_obj)
        ret = client.upload_by_buffer(content.read())
        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")
        file_name = ret.get("Remote file_id")

        # file_name为bytes类型，只能返回str类型，不然会报错
        return file_name.decode()

    def url(self, name):
        """
        返回文件的完整URL路径
        :param name: 数据库中保存的文件名
        :return: 完整的URL
        """
        return self.option.get('BASE_URL') + name

    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件的重名问题
        所以此处返回False，告诉Django上传的都是新文件
        :param name:  文件名
        :return: False
        """
        return False
