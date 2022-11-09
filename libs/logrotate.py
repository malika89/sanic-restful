#!/usr/bin/env python3
"""
lograte the log with custom interval
"""

import os
import shutil
from datetime import datetime, timedelta


def logrotate(target, interval=timedelta(days=1), time_format="%Y%m%d"):
    """
    日志切割
    :param target(str): target folder or log file name
    :param interval(timedelta): time interval of how often the file to be cut
    :param time_format(str): the time format to be used as part of the cutted file name
    :return: None
    """
    if os.path.isfile(target):
        path = ""
        files = [target]
    else:
        path = target if target[-1] == "/" else target + "/"
        files = os.listdir(target)

    for f in files:
        segment = f.split(".")
        if len(segment) != 2 or segment[-1] != "log":
            continue
        flag = (datetime.now() - interval).strftime(time_format)
        src = path + f
        dst = path + f"{segment[0]}.{flag}.{segment[1]}"
        if os.path.exists(dst):
            continue
        shutil.copyfile(src, dst)
        with open(src, "w") as f:
            pass
