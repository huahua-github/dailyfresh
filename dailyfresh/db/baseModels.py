# coding:utf-8
from django.db import models
"""定义模型抽象基类"""
class BaseModel(models.Model):
    # 创建时间
    create_datetime = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    # 修改时间
    update_datetime = models.DateTimeField(auto_now=True,verbose_name="更新时间")
    # 删除标识
    is_delete = models.BooleanField(default=False,verbose_name="删除标记")

    class Meta:
        abstract = True