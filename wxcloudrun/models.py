from datetime import datetime

from django.db import models


# Create your models here.
class Counters(models.Model):
    id = models.AutoField
    count = models.IntegerField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Counters'  # 数据库表名


class Activity(models.Model):
    STATUS_CHOICES = [
        ('published', '已发布'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ]
    TYPE_CHOICES = [
        ('match', '球赛'),
        ('tb', '聚餐'),
        ('other', '其他'),
    ]

    datetime = models.DateTimeField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    headcount = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='other')
    other = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {"id": self.id, "datetime": self.datetime, "location": self.location, "latitude": self.latitude, "longitude": self.longitude,
                "headcount": self.headcount, "comment": self.comment, "status": self.status, "type": self.type,
                "other": self.other, "create_time": self.create_time, "last_update": self.last_update}

    @classmethod
    def get_overview_history_activity(cls):
        qs = cls.objects.all()
        return [{"datetime": obj.datetime, "location": obj.location, "status": obj.status} for obj in qs]

    @classmethod
    def get_exact_history_activity_by_id(cls, activity_id):
        obj = cls.objects.filter(id=activity_id).first()
        joiner_info = [{"nickname": obj.member.nickname, "avatar": obj.member.avatar} for obj in
                       ActivityMember.objects.filter(activity=obj)]
        return {"datetime": obj.datetime, "location": obj.location, "status": obj.status, "comment": obj.comment,
                "type": obj.type, "headcount": len(joiner_info), "joiner_openid": joiner_info}

    def get_activity_all_info(self):
        joiner_info = [
            {
                "nickname": obj.member.nickname,
                "avatar": obj.member.avatar,
                "type": obj.type,
                "openid": obj.member.openid
            } for obj in ActivityMember.objects.filter(activity=self)
        ]
        return {
            "activity_info": {
                "datetime": self.datetime, "location": self.location, "latitude": self.latitude,
                "longitude": self.longitude, "status": self.status, "comment": self.comment,
                "type": self.type, "headcount": self.headcount
            },
            "member_infos": joiner_info
        }

    @classmethod
    def get_all_activity_record(cls):
        qs = Activity.objects.all()
        qs = qs.order_by('-create_time')
        return [{
            "activity_id": obj.id,
            "datetime": obj.datetime,
            "location": obj.location,
            "type": obj.type,
            "status": obj.status
        } for obj in qs]



class Member(models.Model):
    ROLE_CHOICES = [
        ('normal', '普通用户'),
        ('admin', '管理员'),
    ]
    TYPE_CHOICES = [
        ('current', '现役会员'),
        ('retired', '退役会员'),
        ('reserve', '后补会员'),
        ('guest', '散客'),
    ]

    openid = models.CharField(max_length=100)
    avatar = models.CharField(max_length=150, null=True, blank=True)
    nickname = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='guest')
    description = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def to_dict(self):
        res = {"openid": self.openid, "nickname": self.nickname,
               "avatar": str(self.avatar),
               "role": self.role, "type": self.type, "description": self.description,
               "other": self.other, "create_time": str(self.create_time), "last_update": str(self.last_update)}
        return res

    def create_new_member(self, openid, nickname, avatar, _type):
        self.openid = openid
        self.nickname = nickname
        self.avatar = avatar
        self.type = _type
        self.save()

    def create_guest(self, openid, nickname, avatar):
        self.openid = openid
        self.nickname = nickname
        self.avatar = avatar
        self.type = 'guest'
        self.save()


class ActivityMember(models.Model):
    PARTICIPATION_TYPE_CHOICES = [
        ('present', 'present'),
        ('absent', 'absent'),
        ('take_leave', 'take leave'),
    ]

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_member')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='activity_member')
    type = models.CharField(max_length=10, choices=PARTICIPATION_TYPE_CHOICES, default='present')
    other = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    @classmethod
    def get_activity_record_by_openid(cls, openid):
        qs = ActivityMember.objects.filter(member__openid=openid)
        if not qs.exists():
            return []
        qs = qs.order_by('-create_time')
        return [{
            "activity_id": obj.activity.id,
            "datetime": obj.activity.datetime,
            "location": obj.activity.location,
            "type": obj.activity.type,
            "status": obj.activity.status
        } for obj in qs]


class RechargeRecord(models.Model):
    OPERATION_CHOICES = [
        ('cut', 'cut'),
        ('save', 'save'),
    ]
    TYPE_CHOICES = [
        ('match', 'match'),
        ('absent', 'absent'),
        ('take_leave', 'take leave'),
    ]

    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES, default='save')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='save')
    amount = models.IntegerField()
    pay_load = models.IntegerField()
    other = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    @classmethod
    def get_current_info(cls, member_openid):
        qs = RechargeRecord.objects.filter(member__openid=member_openid)
        if not qs.exists():
            return {"activity_count": 0, "pay_load": 0}
        obj = qs.order_by('-create_time')[0]
        return {"activity_count": qs.count(), "pay_load": obj.pay_load}

class Environment(models.Model):
    value = models.CharField(max_length=100, default='dev')
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


    @classmethod
    def get_value(cls):
        return cls.objects.first().value