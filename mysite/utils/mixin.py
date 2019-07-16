from django.contrib.auth.decorators import login_required


class LoginRequiredMixIn(object):
    '''多重继承父类，提供登录跳转'''
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as_view
        view = super(LoginRequiredMixIn, cls).as_view(**initkwargs)
        return login_required(view)
