# coding:utf-8
from celery import Celery
from django.core.mail import send_mail
import time
from dailyfresh.settings import EMAIL_HOST_USER
from django.urls import reverse
import os
import django
from dailyfresh import settings
from apps.user.models import Address
from django.template import loader

'''django环境初始化'''
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')  # 适配windows 环境
django.setup()
app = Celery("celery_tasks.task",broker="redis://127.0.0.1:6379/3")
@app.task
def send_register_email(to_email,active_url):
    """发送激活邮件"""


    # 发送连接到邮箱
    subject = "用户激活"
    message = "<h1>欢迎注册天天生鲜</h1><br>,<span>账号激活地址：</span><br><a href=" + active_url + ">" + active_url + "</a>"
    from_email = EMAIL_HOST_USER
    recipient_list = [to_email]
    time.sleep(10)
    send_mail(subject, "", from_email, recipient_list, html_message=message)
    print("邮件执行完毕")

# @app.task
# def generate_static_userinfo_html(request,context):
#
#     # context = {"addressinfo": address_list, "addrinfo": addrinfo}
#     template = loader.get_template("userinfo.html")
#     userinfo_html = template.render(context)
#     with open(os.path.join(settings.BASE_DIR, "static/html/userinfo_static.html"), 'w', encoding="utf8") as f:
#         f.write(userinfo_html)
#
