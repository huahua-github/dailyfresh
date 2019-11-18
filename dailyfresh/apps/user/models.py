from django.db import models
from db.baseModels import BaseModel
from django.contrib.auth.models import AbstractUser
from django.conf import settings

"""自定义User模型管理类"""
class UserManage(models.Manager):
    # 重写all方法
    def all(self):
        return super(UserManage, self).all().filter(is_delete=False)

    def get_default_addr(self,user):
        try:

            default_addrinfo = list(self.model.objects.all().filter(is_default=True, user=user).values("receiver", "phone", "addr"))[0]
            return default_addrinfo
        except Exception:
            return None


# Create your models here.
class User(AbstractUser,BaseModel):
    """用户模型类"""

    class Meta:
        db_table = "df_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class Address(BaseModel):
    """地址模型类"""
    user = models.ForeignKey("User",on_delete=False,verbose_name="所属账户")
    # 收件人
    receiver = models.CharField(max_length=20,verbose_name="收件人")
    # 收件地址
    addr = models.CharField(max_length=256,verbose_name="收件地址")
    # 邮政编码
    zip_code = models.CharField(max_length=6,verbose_name="邮政编码",null=True)
    # 联系电话
    phone = models.CharField(max_length=11,verbose_name="联系电话")
    # 是否默认
    is_default = models.BooleanField(default=False,verbose_name="是否默认")
    # 自定义管理对象
    objects = UserManage()
    class Meta:
        db_table = "df_address"
        verbose_name = "地址"
        verbose_name_plural = verbose_name
