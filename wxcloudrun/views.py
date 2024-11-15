import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters, Member

logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                    json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                    json_dumps_params={'ensure_ascii': False})

def get_user_info(request):
    """
    获取用户信息

     `` request `` 请求对象
    """
    logger.info('get_user_infoe request: {}'.format(request.headers))
    openid = request.headers.get('X-Wx-openid', "no openid")
    user = Member.objects.filter(openid=openid)
    if not user:
        user_info = {"openid": openid, "nickname": None, "avatar": None,
               "role": "guest", "type": "guest", "description": None,
               "other": None, "create_time": None, "last_update": None}
        return JsonResponse(user_info,
                        json_dumps_params={'ensure_ascii': False})

    user_info = user[0].to_dict()
    return JsonResponse(user_info,
                        json_dumps_params={'ensure_ascii': False})

def apply_join_club(request):
    """
    创建用户

     `` request `` 请求对象
    """
    logger.info('apply_join_club request: {}'.format(request.headers))
    openid = request.headers.get('X-Wx-openid')
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    user = Member.objects.filter(openid=openid)
    if not user:
        user = Member()
        user.create_new_member(openid=openid, nickname=body['nickname'])
    else:
        user = user[0]

    user_info = user.to_dict()
    return JsonResponse(user_info,
                        json_dumps_params={'ensure_ascii': False})