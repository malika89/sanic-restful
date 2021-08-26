#!/usr/bin/env python3
"""
日志分割
"""

import os
import shutil
from datetime import datetime, timedelta


def logrotate(target, interval=timedelta(days=1), time_format='%Y%m%d'):
    """
    日志切割
    :param target(str): 目标文件夹or日志
    :param interval(timedelta): 切割间隔
    :param time_format(str): 文件名日期格式
    :return: None
    """
    if os.path.isfile(target):
        path = ''
        files = [target]
    else:
        path = target if target[-1] == '/' else target + '/'
        files = os.listdir(target)

    for f in files:
        segment = f.split('.')
        if len(segment) != 2 or segment[-1] != 'log':
            continue
        flag = (datetime.now() - interval).strftime(time_format)
        src = path + f
        dst = path + '{}.{}.{}'.format(segment[0], flag, segment[1])
        if os.path.exists(dst):
            continue
        shutil.copyfile(src, dst)
        with open(src, 'w') as f:
            pass