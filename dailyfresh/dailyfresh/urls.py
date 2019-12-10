"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from apps.user import views as userviews
from apps.goods import views as goodviews
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator  # 是将类装饰器转换为方法装饰器

urlpatterns = [
    path('admin/', admin.site.urls),
    path('showregister',userviews.showregister,name="showregister"),
    path('register',userviews.register,name="register"),
    path('showlogin',userviews.showlogin,name="showlogin"),
    path('showregister1',userviews.showregister1.as_view(),name="showregister1"),
    re_path(r'activeusr/(?P<re_str>.*)$',userviews.Activeuser.as_view(),name="activeuser"),
    path('login',userviews.userlogin.as_view(),name="login"),
    # re_path(r'^showindex',login_required(userviews.showindex.as_view()),name="showindex"),
    # path('showcart',login_required(userviews.showcart.as_view()),name="showcart"),
    re_path(r'^showindex',userviews.showindex.as_view(),name="showindex"),
    path('showcart',userviews.showcart.as_view(),name="showcart"),
    path('logout',userviews.userlogout.as_view(),name="logout"),
    path('showuserinfo',userviews.userinfo.as_view(),name="showuserinfo"),
    path('adduserinfo',userviews.adduserinfo.as_view(),name="adduserinfo"),
    path('uploadfile',goodviews.uploadfile.as_view(),name="uploadfile"),
    path('showuploadhtml',goodviews.showuploadhtml.as_view(),name="showuploadhtml"),
    path('showhistory',goodviews.showhistory.as_view(),name="showhistory")
]
