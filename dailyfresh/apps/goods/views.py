from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from utils.loginrequriedUtil import LoginRequiredMixin
from django.views.generic import View
from dailyfresh import settings
import os
import re
from PIL import Image
import dhash
import redis
from django_redis import get_redis_connection
from apps.goods.models import GoodsType,GoodsSKU,Goods
from django.core.serializers import serialize
import json
import hashlib
# Create your views here.
class uploadfile(LoginRequiredMixin,View):

    def post(self,request):
        # 商品类型参数
        typename = request.POST.get("typename")
        logo = request.POST.get("logo")
        typeimage = request.FILES.get("typeimage",None)
        image_name = typeimage.name
        print(image_name)
        imagetype = image_name.split(".")[1]
        print(imagetype)
        pimage = Image.open(typeimage)
        print(dhash.dhash_row_col(pimage))
        row , col=dhash.dhash_row_col(pimage)
        str = dhash.format_hex(row,col)
        types = GoodsType.objects.all().filter(is_delete=False)
        check = False
        goodtype=None
        for type in types:
            print(type.image.url)
            imagename=re.match(r"^.+/(.+)\.[a-z]+$",type.image.url).group(1)
            print(imagename)
            print(str)
            if imagename==str:
                check = True
                goodtype=type
                break


        if not check :
            print("------------------+++++++++++++++++")
            with open(os.path.join(settings.MEDIA_ROOT,str+"."+imagetype),'wb') as f:
                for chunk in typeimage.chunks():
                    f.write(chunk)
            goodtype = GoodsType()
            goodtype.name = typename
            goodtype.logo = logo
            typeimage.name = str+"."+imagetype
            goodtype.image = typeimage
            goodtype.save()
        # SPU参数
        spuname = request.POST.get("spuname")
        spudisc = request.POST.get("disc")
        goodspu = Goods()
        goodspu.name = spuname
        goodspu.detail = spudisc
        goodspu.save()
        # SKU参数
        skuname = request.POST.get("skuname")
        simpdisc = request.POST.get("simpdisc")
        price = float(request.POST.get("price"))
        danwei  = request.POST.get("danwei")
        imagefile = request.FILES.get("imagefile")
        imagename = imagefile.name
        print("++++++++++++++++++++")
        print(imagename)
        imagetype = imagename.split(".")[1]
        row1 , col1 = dhash.dhash_row_col(Image.open(imagefile))
        str1 = dhash.format_hex(row1,col1)
        skus = GoodsSKU.objects.all().filter(is_delete=False)
        check01 = False
        goodsku = None
        for sku in skus:
            imagename = re.match(r"^.+/(.+)\.[a-z]+$", sku.image.url).group(1)
            print(str1)
            print(imagename)
            if imagename == str1:
                check01 = True
                goodsku = sku
                break

        kucun = int(request.POST.get("kucun"))
        totle = int(request.POST.get("totle"))
        status = request.POST.get("status")
        goods = Goods.objects.all().filter(name=spuname)[0]
        print(check01)
        if not check01:
            print("------------------00000000000000000")
            print(str1)
            with open(os.path.join(settings.MEDIA_ROOT, str1+"."+imagetype), 'wb') as f:
                for chunk in imagefile.chunks():
                    f.write(chunk)
            goodsku = GoodsSKU()
        goodsku.name = skuname
        goodsku.desc = simpdisc
        goodsku.price = price
        goodsku.unite = danwei
        imagefile.name = str1+"."+imagetype
        goodsku.image = imagefile
        goodsku.stock = kucun
        goodsku.sales = totle
        goodsku.status = status
        goodsku.goods = goods
        goodsku.type = goodtype

        goodsku.save()
        return JsonResponse({"message":"上传成功"})


class showuploadhtml(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,"uploadimage.html")


class showhistory(LoginRequiredMixin,View):
    def get(self,request):
        id = request.GET.get("id")
        # redis1 = get_redis_connection("default")
        redis1 = redis.Redis("127.0.0.1",6379,0,decode_responses=True)
        key = request.user.username+"history"
        redis1.lpush(key,id)
        redis1.expire(key,3600)
        infos = list()
        for v in redis1.lrange(key,0,-1):
            print(v)
            infos.append(v)

        return HttpResponse(json.dumps({"message":"OK","info":infos}))