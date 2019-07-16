from django.shortcuts import Http404


class PoolEmptyError(Http404):

    def __init__(self):
        Http404.__init__(self)

    def __str__(self):
        return repr('代理池已经枯竭')
