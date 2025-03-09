import re

from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http import JsonResponse

# Create your views here.
"""
需求分析： 根据页面的功能（从上到下，从左到右），哪些功能需要和后端配合完成

"""

"""
判断用户名是否重复的功能。
前端：当用户输入用户名之后，失去焦点，发送一个axios(ajax)请求

后端：
    请求：   接收用户名
    业务逻辑： 根据用户名查询数据库，如果查询结果数量等于0，说明没有注册，
             如果查询结果数量等于1，说明有注册。
    响应：  JSON
            {code:0,count:0/1,errmsg:ok}
    
    路由：   GET    /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    步骤：
           1.接收用户名
           2.根据用户名查询数据库
           3.返回响应
"""


class UsernameCountView(View):
    @staticmethod
    def get(request, username):
        """
           1.接收用户名，对用户名进行一个判断
           2.根据用户名查询数据库
           3.返回响应
        """
        # if not re.match('^[a-zA-Z0-9_-]{5,20}', username):
        #     return JsonResponse({'code': 200, 'errmsg': '用户名不满足需求'})

        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})


import json


class RegisterView(View):
    @staticmethod
    def post(request, *args, **kwargs):
        body_byte = request.body
        body_str = body_byte.decode('utf-8')
        body_dict = json.loads(body_str)

        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # all([xxx,xxx,xxx])
        # all 里的元素 只要是 None, False
        # all 就返回False 否则返回True
        if not all([username, password, password2, mobile,allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        if not re.match('[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足'})
        # if not re.match('[0-9_-]{11}', mobile):
        #     return JsonResponse({'code': 400, 'errmsg': '手机号不正确'})
        #
        # if allow == 'true':
        #     return JsonResponse({'code': 400, 'errmsg': '未允许协议'})

        # 方式一
        # user = User(username=username, password=password, mobile=mobile)
        # user.save()

        # User.objects.create(username=username, password=password, mobile=mobile)

        # 方式二
        User.objects.create_user(username=username, password=password, mobile=mobile)

        # 以上两种方式，都可以数据库入库
        # 但是 有一个问题 方式一 密码没有加密

        # 设置session信息
        # request.session['user_id'] = user.id

        # 系统(Django) 为我们提供了 状态保存的方法
        from django.contrib.auth import login
        # request, user
        # 状态保持 -- 登录用户的状态保持
        # user 已经登录的用户信息
        login(request, username)


        return JsonResponse({'code': 0, 'errmsg': 'ok'})

"""
如果需求是注册成功后即表示用户认证通过，那么此时可以在注册成功后实现状态保持
如果需求是注册成功后不表示用户认证通过，那么此时不用在注册成功后实现状态保持

实现状态保持主要有两种方式：
    在客户端存储信息使用Cookie
    在服务器端存储信息使用Session
"""