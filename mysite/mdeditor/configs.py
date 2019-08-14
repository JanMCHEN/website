# coding:utf-8
from django.conf import settings


DEFAULT_CONFIG = {
    'width': '100%',
    'height': 500,
    'toolbar': ["undo", "redo", "|",
                "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                "h1", "h2", "h3", "h5", "h6", "|",
                "list-ul", "list-ol", "hr", "|",
                "link", "reference-link", "image", "code", "preformatted-text", "code-block", "table", "datetime",
                "emoji", "html-entities", "pagebreak", "goto-line",
                "||", "preview", "watch", "fullscreen", "help", "info", ],
    'upload_image_formats': ["jpg", "JPG", "jpeg", "JPEG", "gif", "GIF", "png",
                             "PNG", "bmp", "BMP", "webp", "WEBP"],
    'image_folder': 'editor',
    'theme': 'default',  # dark / default
    'preview_theme': 'dark',  # dark / default
    'editor_theme': 'default',  # pastel-on-dark / default
    'toolbar_autofixed': True,
    'search_replace': True,
    'emoji': True,
    'tex': True,
    'flow_chart': True,
    'sequence': True,
    'language': 'zh',  # zh / en
    'watch': True,  # Live preview
    'lineWrapping': False,  # lineWrapping
    'lineNumbers': False  # lineNumbers
}


class MDConfig(dict):

    def __init__(self, config_name=None):
        self.update(DEFAULT_CONFIG)
        self.set_configs(config_name)

    def set_configs(self, config_name=None):
        """
        set config item
        :param config_name:
        :return:
        """
        # Try to get valid config from settings.
        configs = getattr(settings, 'MDEDITOR_CONFIGS', None)
        if configs and config_name:
            assert isinstance(configs, dict), 'MDEDITOR_CONFIGS must be a dict'
            config = configs.get(config_name, None)
            assert isinstance(config, dict), 'MDEDITOR_CONFIGS["%s"] setting must be a dictionary.' % config_name
            self.update(config)

