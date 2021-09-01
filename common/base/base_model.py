#!/usr/bin/python
# coding:utf-8

from tortoise import Model, fields


class BaseModel(Model):

    CHOICES = {}
    FOREIGN_KEYS = {}

    id = fields.IntField(pk=True)
    create_time = fields.DatetimeField(50,description="创建时间")
    update_time = fields.DatetimeField(50, description="修改时间")
    create_by = fields.CharField(50, null=False, default="", description="创建人")
    update_by = fields.CharField(50, null=False, default="", description="修改人")
    is_deleted = fields.BooleanField(default=False, description="是否被删除")

    class Meta:
        abstract = True
        ordering = ["-update_time", "id"]

    def __str__(self):
        return str(self.id)


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
