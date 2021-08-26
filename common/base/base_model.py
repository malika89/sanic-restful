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