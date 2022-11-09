#!/usr/bin/python

import logging
import os
import sys
from datetime import datetime


class Log:
    PATH = sys.path[0] + "/logs/"
    LOG_FILE = "{}{}.log".format(PATH, datetime.now().strftime("%Y%m%d"))
    LOG_FORMAT = "%(asctime)sの%(levelname)sの%(name)sの%(pathname)s(line:%(lineno)d)の%(message)s"

    def __init__(self):
        pass

    def get_level(self, level):
        if level == "debug":
            rep = logging.DEBUG
        elif level == "info":
            rep = logging.INFO
        elif level in ["warnning", "warn"]:
            rep = logging.WARN
        elif level == "error":
            rep = logging.ERROR
        elif level == "critical":
            rep = logging.CRITICAL
        return rep

    def file_handler(self, logfile=LOG_FILE):
        if not os.path.isdir(self.PATH):
            os.makedirs(self.PATH)
        _format = self.LOG_FORMAT
        handler = logging.FileHandler(logfile)
        formatter = logging.Formatter(_format)
        handler.setFormatter(formatter)
        return handler

    def stream_handler(self):
        _format = self.LOG_FORMAT
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_format)
        handler.setFormatter(formatter)
        return handler

    def print_handler(self):
        _format = "%(message)s"
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_format)
        handler.setFormatter(formatter)
        return handler

    def file_logger(self, obj="__main__", level="info", logfile=LOG_FILE):
        handler = self.file_handler(logfile)
        logger = logging.getLogger(obj)
        logger.setLevel(self.get_level(level))
        logger.addHandler(handler)
        return logger

    def stream_logger(self, obj="__main__", level="info"):
        handler = self.stream_handler()
        logger = logging.getLogger(obj)
        logger.setLevel(self.get_level(level))
        logger.addHandler(handler)
        return logger

    def print_logger(self, obj="__main__", level="info"):
        handler = self.print_handler()
        logger = logging.getLogger(obj)
        logger.setLevel(self.get_level(level))
        logger.addHandler(handler)
        return logger
