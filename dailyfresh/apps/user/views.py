import os

from django.shortcuts import render,redirect
from apps.user.models import User
from apps.user.models import Address
from django.http import HttpResponse,JsonResponse,response
from django.views.generic import View
from django.urls import reverse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from dailyfresh.settings import SECRET_KEY,EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
import time
import json
from django.core.serializers import serialize
from celery_tasks.task import send_register_email
from utils.loginrequriedUtil import LoginRequiredMixin
from django.template import loader
from dailyfresh import settings
# from celery_tasks.task import generate_static_userinfo_html
# Create your views here.
# /showregister
def showregister(request):
    """函数视图"""
    return render(request,"register.html")
# /showregister1
class showregister1(View):
    """类视图"""
    def get(self,request):
        print("+"*50)
        return render(request,"register.html")

    def post(self,request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        repassword = request.POST.get("repassword")
        email = request.POST.get("email")
        acept = request.POST.get("access")
        if all([username, password, repassword, email]):
            if password != repassword:
                return JsonResponse({"message": "两次输入的密码不一致"})
            try:
                user = User.objects.get(username=username)
            except Exception as e:
                user = None
            if user:
                return JsonResponse({"message": "用户已存在"})
            user = User.objects.create_user(username, password, email)
            user.is_active = 0
            user.save()
            return JsonResponse({"message": "OK"})
        else:
            return JsonResponse({"message": "输入的数据不完整"})

# /register
def register(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    repassword = request.POST.get("repassword")
    email = request.POST.get("email")

    acept = request.POST.get("access")
    if all([username,password,repassword,email]):
        if password!=repassword:
            return JsonResponse({"message":"两次输入的密码不一致"})
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            user=None
        if user:
            return JsonResponse({"message":"用户已存在"})
        user = User.objects.create_user(username=username,password=password,email=email)
        user.is_active=0
        user.save()
        # 生成激活连接
        user = User.objects.get(username=username)
        userId = user.id
        useremail = user.email
        user_dict = {"userId":userId}
        serializer = Serializer(SECRET_KEY,3600)
        re_str = serializer.dumps(user_dict).decode()
        active_url = "http://"+request.get_host()+reverse("activeuser",kwargs={"re_str":re_str})
        try:
            print("异步任务执行前---------------------------")
            send_register_email.delay(useremail,active_url)
            print("异步任务执行后---------------------------------------")
        except Exception as e:
            return JsonResponse({"message": "邮箱发送出错"})
        # # 发送连接到邮箱
        # subject = "用户激活"
        # message = "<h1>欢迎注册天天生鲜</h1><br>,<span>账号激活地址：</span><br><a href="+active_url+">"+active_url+"</a>"
        # from_email = EMAIL_HOST_USER
        # recipient_list = [useremail]
        # try:
        #     time.sleep(5)
        #     send_mail(subject,"",from_email,recipient_list,html_message=message)
        # except Exception as e:
        #     return JsonResponse({"message":"邮箱发送出错"})

        print("++++++++++++++++++++++++++++++++")
        return JsonResponse({"message":"OK"})
    else:
        return JsonResponse({"message":"输入的数据不完整"})



class Activeuser(View):
    def get(self,request,re_str):
        serializer = Serializer(SECRET_KEY,3600)
        userId = serializer.loads(re_str)["userId"]

        user = User.objects.get(id=userId)
        user.is_active = 1
        username = user.username
        useremail = user.email
        user.save()
        subject="账号激活"
        message = "尊敬的用户:"+username+"，你的天天生鲜账号激活成功可以登录"
        from_email = EMAIL_HOST_USER
        recipient_list = [useremail]
        try:
            print("++++++++++++++++++++++++")
            send_mail(subject,message,from_email,recipient_list)
            print("----------------------------")
        except Exception as e:
            return HttpResponse("邮件发送失败")
        return HttpResponse("激活成功")


# /showlogin
def showlogin(request):
    username = request.COOKIES.get("username")
    next_url = request.GET.get("next","showindex")
    if username!=None:
        return render(request,"login.html",{"username":username,"checked":"checked","next_url":next_url})
    return render(request,"login.html",{"next_url":next_url})


# /login
class userlogin(View):
    """登陆类视图"""
    def get(self,request):
        pass
    def post(self,request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        merusername = request.POST.get("merusername")

        # user = User.objects.get(username=username,password=password)
        user = authenticate(username=username,password=password)  # django认证机制内置
        if user!=None:
            if user.is_active:
                login(request,user)
                if merusername=="true":

                    response = JsonResponse({"message": "OK", "username": username})
                    response.set_cookie("username",username)
                else:
                    print("==================")
                    response = JsonResponse({"message": "OK", "username": username,})
                    response.delete_cookie("username")
                return response
            else:
                return JsonResponse({"message":"账号尚未激活不能登陆"})

        else:
            return JsonResponse({"message":"用户名或密码错误"})


# /showindex
class showindex(LoginRequiredMixin,View):
    def get(self,request):
        """如果用户登陆返回一个User实例，如果没有登陆返回一个AnonymousUser实例"""
        """除了返回模板以外还返回request.user传给模板文件，所以可以通过user.is_Authenticated返回的是否是USer
        实例来判断用户是否登陆，如果登陆可以通过user.username获取用户名"""
        return render(request,"index.html")


# /showcart
class showcart(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,"product_cart.html")


# /logout
class userlogout(View):
    def get(self,request):
        logout(request)
        return redirect(reverse("showlogin"))

"""/showuserinfo---个人中心"""
class userinfo(LoginRequiredMixin,View):

    def get(self,request):
        # 获取收货地址列表
        address_list = Address.objects.all().filter(user=request.user)
        addrinfo = Address.objects.get_default_addr(request.user)
        context={"addressinfo":address_list,"addrinfo":addrinfo}
        #
        # template = loader.get_template("userinfo.html")
        # userinfo_html = template.render(context)
        # with open(os.path.join(settings.BASE_DIR,"static/html/userinfo_static.html"),'w',encoding="utf8") as f:
        #     f.write(userinfo_html)
        # generate_static_userinfo_html.delay(request,context)
        return render(request,"userinfo.html",{"addressinfo":address_list,"addrinfo":addrinfo})

"""/adduserinfo----增加收货地址信息"""
class adduserinfo(LoginRequiredMixin,View):
    def post(self,request):

        addr = request.POST.get("address")

        receiver = request.POST.get("receiver")

        zip_code = request.POST.get("zip_code")
        phone = request.POST.get("phone")

        user = request.user
        try:
            useraddr = Address.objects.get(user=user)
        except Exception:
            useraddr = None
        address = Address()
        if all([address,receiver,phone]):
            address.user = user
            address.addr = addr
            address.receiver = receiver
            address.zip_code = zip_code
            address.phone = phone
            if useraddr == None:
                address.is_default=True
            address.save()
            """
            json序列化：1、当查询结果是queryset时需要用serialize方法进行序列化
            2、当查询结果是valuequeryset时将结果集装换为list类型后用json.dumps方法序列化
            
            """
            addrinfo = Address.objects.get_default_addr(request.user)
            addre_list =list(Address.objects.all().filter(user = user).values("addr","receiver","phone"))
            message = {"message":"OK"}
            addre_list.append(message)
            return HttpResponse(json.dumps({"json_data":addre_list,"message":"OK","addrinfo":addrinfo}))
        else:
            return JsonResponse({"message":"表单数据不完整！"})
