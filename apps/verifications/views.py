from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

"""

 url=http://ip:port/image_codes/uuid/

步骤：
    1. 接收路由中的uuid
    2. 生成图片验证码和图片二进制
    3. 通过redis把图片验证码保存起来
    4. 返回图片二进制

"""


# Create your views here.
class ImageCodeView(View):

    def get(self, request, uuid):
        # 1.接收路由中的uuid
        # 2.生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text 是图片验证码的内容 例如： xyzz
        # image 是图片二进制
        text, image = captcha.generate_captcha()
        # 3.通过redis把图片验证码保存起来
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex(uuid, 300, text)
        # 4.返回图片二进制
        return HttpResponse(image, content_type='image/jpeg')
