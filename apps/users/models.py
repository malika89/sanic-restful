#!/usr/bin/python
# coding:utf-8


from common.base.base_model import BaseModel
from tortoise import fields


class Users(BaseModel):
    CHOICES = {
        "sex": (
            (1, "男"),
            (2, "女"),
        )
    }
    name = fields.CharField(100, null=False, default="", description="姓名")
    identity = fields.CharField(20, null=False, default="",unique=True, description="证件号")
    sex = fields.SmallIntField(pk=False,choices=CHOICES["sex"], default=1, description="性别")
    age = fields.IntField(description="年龄")
    nationlity = fields.CharField(50, null=False, default="", description="国籍")

    class Meta:
        table = "users"


    def to_dict(self,only=None,exclude=None):
        if only:
            columns = only
        elif exclude:
            columns = exclude
        else:
            columns = self._meta.fields
        data = dict()
        for field in columns:
            field_type = self._meta.fields[field]
            value = getattr(self,field)
            if isinstance(field_type,fields.DatetimeField):
                data.update({field:value.strftime("%Y-%m-%d %H:%M:%S") if value else ""})
            elif isinstance(field_type,fields.DateField):
                data.update({field:getattr(self,field).strftime("%Y-%m-%d") if value else "" })
            else:
                data.update({field:value})
        return data
