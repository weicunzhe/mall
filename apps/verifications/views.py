from django.http import HttpResponse, JsonResponse
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


class SmsCodeView(View):
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('verify_codes')
        redis_image_code = redis_conn.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图形验证码已过期'})
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图形验证码不正确'})

        # 提取发送短信标记，判断是否发送过
        send_flag = redis_conn.get('send_flag_' % mobile, 60, 1)
        if send_flag is not None:
            return JsonResponse({'code': 400, 'errmsg': '不要频繁发送短信'})

        from random import randint
        sms_code = '%04d' % randint(0, 9999)
        redis_conn.setex(mobile, 300, sms_code)
        # 添加一个发送标记,有效期60秒
        redis_conn.setex('send_flag_' % mobile, 60, 1)
        from libs.sms import SmsSDK

        accId = '2c94811c946f6bfb0195846f61952b7b'
        accToken = '6ccc2e2111c0408e96cff3e484c2fb6d'
        appId = '2c94811c946f6bfb0195846f63402b82'
        sdk = SmsSDK(accId, accToken, appId)
        tid = '1'
        mobile = '18309252173'
        datas = (sms_code, '5')
        resp = sdk.sendMessage(tid, mobile, datas)
        print(resp)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
