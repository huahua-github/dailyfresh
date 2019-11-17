# coding:utf-8
from django.contrib.auth.decorators import login_required

class LoginRequiredMixin(object):
    """使用继承LoginRequiredMixin类的方式实现login_required 校验是否登陆并返回next参数"""
    @classmethod
    def as_view(cls,**initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)