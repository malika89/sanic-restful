#!/usr/bin/env python3
"""
convert libs, the method includes:
   + model and data transformation
   + data type conversion

"""

import os
import time
from datetime import date,datetime
from tortoise.models import ForeignKey, ManyToManyField, DateTimeField, DateField, SmallIntegerField, QuerySet,DecimalField
from itertools import chain
from functools import wraps


TIME_FORMAT_YMD_DASH_DATETIME = '%Y-%m-%d %H:%M:%S'


def is_empty(value):
    """check if value is empty"""
    if value is None:
        return True
    if value == '':
        return True
    if str(value).strip() == '':
        return True
    return False


def check_local_dir(local_path):
    try:
        os.makedirs(local_path, mode=0o755, exist_ok=True)
        return True
    except:
        return False

def char_has_special_char(desstr, restr=''):
    import re
    # Filter other characters except Chinese, English and numbers
    res = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
    s = res.sub(restr, desstr)
    if s != desstr:
        return True
    else:
        False


def char_has_chinese(text):
    # for python 3.x
    # sample: char_has_chinese('一') == True, char_has_chinese('我&&你') == True
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def date_time(format_type=TIME_FORMAT_YMD_DASH_DATETIME):
    today = time.strftime(format_type)
    return today


def datetime_to_str(timeobj):
    """
    :param timeobj: 'datetime.date'> 2018-12-20
    :return:
    """
    if isinstance(timeobj, datetime):
        return timeobj.strftime(TIME_FORMAT_YMD_DASH_DATETIME)
    elif isinstance(timeobj, date):
        return timeobj.strftime('%Y-%m-%d')
    else:
        return str(timeobj)


def today_date(format_type='%Y-%m-%d'):
    today = time.strftime(format_type)
    return today


def model_to_str(instance, fields=None, exclude=None, has_address=False, hans=False):
    '''
    :param instance:
    :param fields:
    :param exclude:
    :param has_address:
    :return:
    '''
    opts = instance._meta
    data = {}
    DATE_TIME_FIELDS = (DateTimeField, DateField)
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        fname = f.verbose_name if hans else f.name
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        value_object = f.value_from_object(instance)
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[fname] = []
            else:
                data[fname] = list({'id': o.id, 'name': o.__str__()} for o in value_object)
        elif isinstance(f, ForeignKey):
            if instance.pk is None:
                data[fname] = []
            else:
                try:
                    fvalue = getattr(instance, f.name)
                    data[fname] = fvalue.__str__() if fvalue else ''
                except Exception as e:
                    data[fname] = "数据不存在"
        elif isinstance(f, SmallIntegerField):
            if f.choices and value_object or value_object == 0:
                try:
                    data[fname] = dict(f.choices)[value_object]
                except:
                    continue
            else:
                data[fname] = value_object
        elif isinstance(f, DATE_TIME_FIELDS):
            if value_object is not None:
                data[fname] = datetime_to_str(value_object)
            else:
                data[fname] = "1970-01-01"

        elif isinstance(value_object, QuerySet):
            data[fname] = [
                model_to_str(obj,exclude=['create_time', 'update_time']) for
                obj in value_object]
        else:
            data[fname] = value_object
    return data


def fields_verbosename_map(obj, exclude=None):
    '''
    :param obj: Models
    :param exclude: fields name of Models
    :return:
    '''
    fields = {}
    for field in obj._meta.fields:
        if exclude and field.name in exclude:
            continue
        fields[field.name] = field.verbose_name
    return fields


def model_to_dict(instance, fields=None, exclude=None):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        value_object = f.value_from_object(instance)
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list({'id': o.id, 'name': o.__str__()} for o in value_object)
        elif isinstance(f, ForeignKey):
            if instance.pk is None:
                data[f.name] = []
            else:
                try:
                    data[f.name + '_id'] = instance.id
                    data[f.name + '__obj_name'] = getattr(instance,f.name).__str__()
                except Exception as e:
                    data[f.name + '_id'] = instance.id
                    data[f.name+ '__obj_name'] = "Object not exist"
        elif isinstance(f, DecimalField):
            if value_object is not None:
                data[f.name] = str(value_object)
            else:
                data[f.name] = None
        elif isinstance(f, (DateTimeField, DateField)):
            if value_object is not None:
                data[f.name] = datetime_to_str(value_object)
            else:
                data[f.name] = None
        elif isinstance(value_object, QuerySet):
            data[f.name] = [
                model_to_dict(obj, exclude=['create_time', 'update_time']) for obj in value_object]
        else:
            data[f.name] = value_object
    return data


def time_function(func):
    """
    Used as a decorator, returns the time it takes for the function to execute
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'the func run with time :{func.__name__} ： {end-start}')
        return result
    return wrapper


def getIndex(lst, val, whichKey=None):
    """

    :param lst: dict list ,eg [{"key":"val"}]
    :param val: dict value to be searched
    :param whichKey: dict key to be showned,
    :return: 返回(index,dict)
    """
    l = []
    for i in range(len(lst)):
        if lst[i][whichKey] == val:
            l.append((i, lst[i]))
    return l


def get_columns(instance, exclude=[]):
    """
    get the model fields and description ,using as column for record data to  export/import to a file
    获取model 字段和中文名字典，用于导入导出
    :param instance:
    :param exclude:
    :return:
    """
    fields = {}
    for field in instance._meta.fields:
        if exclude and field.name in exclude:
            continue
        fields[field.name] = field.verbose_name
    return fields

