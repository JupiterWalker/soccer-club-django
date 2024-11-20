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
    headcount = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='other')
    other = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


class Member(models.Model):
    ROLE_CHOICES = [
        ('normal', '普通用户'),
        ('admin', '管理员'),
    ]
    TYPE_CHOICES = [
        ('current', '现役会员'),
        ('retired', '退役会员'),
        ('reserve', '后补会员'),
    ]

    openid = models.CharField(max_length=100)
    avatar = models.CharField(max_length=100, null=True, blank=True)
    nickname = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='reserve')
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

    def create_new_member(self, openid, nickname, avatar):
        self.openid = openid
        self.nickname = nickname
        self.avatar = avatar
        self.save()


class ActivityMember(models.Model):
    PARTICIPATION_TYPE_CHOICES = [
        ('present', 'present'),
        ('absent', 'absent'),
        ('take_leave', 'take leave'),
    ]

    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=PARTICIPATION_TYPE_CHOICES, default='present')
    other = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


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
