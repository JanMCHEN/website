from haystack import indexes
from .models import Articles


class ArticlesIndex(indexes.SearchIndex, indexes.Indexable):
    '''# 类名没要求'''
    # use_templates指定根据那些字段建里索引文件，把说明放在一个文件中
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回模型类
        return Articles

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_secret=False)
