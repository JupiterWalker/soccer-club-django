import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters, Member, RechargeRecord, ActivityMember, Activity

logger = logging.getLogger('log')

def add_request_log(request):
    logger.info('get_user_info request url: {},\n'
                'method: {},\n'
                'headers: {},\n'
                'body: {}'.format(request.path_info, request.method, request.headers, request.body))

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

def set_user_info(request):
    """
    配置用户信息

     `` request `` 请求对象
    """
    add_request_log(request)
    assert request.method == 'PUT', 'only PUT method is allowed'
    openid = request.headers.get('X-Wx-openid', "no openid")
    user_info = json.loads(request.body)
    users = Member.objects.filter(openid=openid)
    if not users.exists():
        user = Member()
        user.create_new_member(openid=openid, nickname=user_info.get('nickname', "未命名"),
                               avatar=user_info.get('avatar', "未命名"))
    else:
        users.update(**user_info)
        user = users[0]
    user_info = user.to_dict()
    return JsonResponse(user_info,
                        json_dumps_params={'ensure_ascii': False})

def get_user_info(request):
    """
    获取用户信息

     `` request `` 请求对象
    """
    add_request_log(request)
    openid = request.headers.get('X-Wx-openid', "no openid")
    user = Member.objects.filter(openid=openid)
    if not user:
        user_info = {"openid": openid, "nickname": "unknown guest", "avatar": None,
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
    add_request_log(request)
    openid = request.headers.get('X-Wx-openid') or request.META["headers"].get('X-Wx-openid')
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    user = Member.objects.filter(openid=openid)
    if not user:
        user = Member()
        user.create_new_member(openid=openid, nickname=body['nickname'], avatar=body['avatar'])
    else:
        user = user[0]

    user_info = user.to_dict()
    return JsonResponse(user_info,
                        json_dumps_params={'ensure_ascii': False})



def get_overview_history_activity(request):
    """
    获取历史活动

     `` request `` 请求对象
    """
    add_request_log(request)
    activity_history = Activity.get_overview_history_activity()
    return JsonResponse({'activity_history': activity_history},
                        json_dumps_params={'ensure_ascii': False})

def get_exact_history_activity(request, activity_id):
    """
    获取某一活动的详细信息

     `` request `` 请求对象
    """
    add_request_log(request)
    activity_info = Activity.get_exact_history_activity_by_id(activity_id)
    return JsonResponse({'activity_detailed_info': activity_info},
                        json_dumps_params={'ensure_ascii': False})


def get_activity_info(activity_id):
    """
    获取某一活动的详细信息

     `` request `` 请求对象
    """
    activity_all_info = Activity.objects.get(id=activity_id).get_activity_all_info()
    return activity_all_info

def activity(request, activity_id=None):
    """
    活动

     `` request `` 请求对象
    """
    add_request_log(request)
    if request.method == "GET":
        if activity_id:
            data = get_activity_info(activity_id)
        else:
            data = Activity.get_all_activity_record()
        return JsonResponse(data,
                     json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        dicted_body = json.loads(request.body)
        obj = Activity.objects.create(
            datetime=dicted_body['datetime'], location=dicted_body['location'],
            latitude=dicted_body['latitude'], longitude=dicted_body['longitude'],
            headcount=dicted_body['headcount'], comment=dicted_body['comment'],
            type=dicted_body['type'], other=dicted_body.get('other', "{}")
        )
        return JsonResponse({'activity_id': obj.id},
                            json_dumps_params={'ensure_ascii': False})

    elif request.method == "PUT":
        dicted_body = json.loads(request.body)
        obj = Activity.objects.filter(id=dicted_body['activity_id']).update(**dicted_body)
        activity_info = obj.get_exact_history_activity_by_id()
        return JsonResponse({'activity_detailed_info': activity_info},
                            json_dumps_params={'ensure_ascii': False})

def member_activity(request):
    """
    会员活动

     `` request `` 请求对象
    """
    add_request_log(request)
    if request.method == "GET":
        openid = request.headers.get('X-Wx-openid') or request.META["headers"].get('X-Wx-openid')
        charge_info = RechargeRecord.get_current_info(openid)
        activity_history = ActivityMember.get_activity_record_by_openid(openid)
        return JsonResponse({'charge_info': charge_info, 'activity_history': activity_history},
                                json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        dicted_body = json.loads(request.body)
        activity = Activity.objects.get(id=dicted_body['activity_id'])
        member = Member.objects.get(openid=dicted_body['openid'])
        activity_member = ActivityMember.objects.create(activity=activity, member=member)
        objs = ActivityMember.objects.filter(activity=activity)
        member_infos = [{"avatar": obj.member.avatar, "nickname": obj.member.nickname, "type": obj.type} for obj in objs]

        return JsonResponse({'activity_member_id':activity_member.id, 'activity': activity.to_dict(),
                             "member_infos": member_infos},
                            json_dumps_params={'ensure_ascii': False})
    elif request.method == "PATCH":
        dicted_body = json.loads(request.body)
        activity = Activity.objects.get(id=dicted_body['activity_id'])
        activity_member = ActivityMember.objects.get(id=dicted_body['activity_member_id'])
        activity_member.type = dicted_body['type']
        activity_member.save()
        member_infos = [
            {
                "avatar": obj.member.avatar,
                "nickname": obj.member.nickname,
                "type": obj.type
            } for obj in ActivityMember.objects.filter(activity=activity)
        ]
        return JsonResponse({'activity_member_id':activity_member.id, 'activity': activity.to_dict(),
                             "member_infos": member_infos},
                            json_dumps_params={'ensure_ascii': False})