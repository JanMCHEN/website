# -*- coding:utf-8 -*-
from __future__ import absolute_import

from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from django.forms.utils import flatatt

from .configs import MDConfig


class MDEditorWidget(forms.Textarea):
    """
    Widget providing Editor.md for Rich Text Editing.
    see Editor.md docs: https://pandao.github.io/editor.md/examples/index.html
    """
    def __init__(self, config_name='', *args, **kwargs):
        super(MDEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = MDConfig(config_name)

    def render(self, name, value, renderer=None, attrs=None):
        """
        renderer: django2.1 新增加的参数，此处不做应用，赋值None做兼容处理
        """
        if value is None:
            value = ''

        final_attrs = self.build_attrs(self.attrs, attrs, name=name)
        return mark_safe(render_to_string('markdown.html', {
            'final_attrs': flatatt(final_attrs),
            'value': conditional_escape(force_text(value)),
            'id': final_attrs['id'],
            'config': self.config,
        }))

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        """
        Helper function for building an attribute dictionary.
        This is combination of the same method from Django<=1.10 and Django1.11+
        """
        attrs = dict(base_attrs, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        return attrs

    @property
    def media(self):
        return forms.Media(
            css={
                "all": ("mdeditor/css/editormd.css",)
            },
            js=(
                "mdeditor/js/jquery.min.js",
                "mdeditor/js/lib/codemirror/codemirror.min.js",
                "mdeditor/js/lib/codemirror/addons.min.js",
                "mdeditor/js/lib/codemirror/modes.min.js",
                "mdeditor/js/lib//marked.min.js",
                "mdeditor/js/lib/prettify.min.js",
                "mdeditor/js/lib/raphael.min.js",
                "mdeditor/js/lib/underscore.min.js",
                "mdeditor/js/lib/sequence-diagram.min.js",
                "mdeditor/js/lib/flowchart.min.js",
                "mdeditor/js/lib/jquery.flowchart.min.js",


                "mdeditor/js/editormd.min.js",


            ))
