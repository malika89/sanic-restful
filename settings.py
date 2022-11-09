#!/usr/bin/python

import configparser

from common.logger import Log

installed_apps = ["apps.regions", "apps.zones"]


config = configparser.ConfigParser()
config.read("conf.ini")

# log settings
CURRENT_ENV = config["common"]["env"]
LOG_PATH = config["log"]["log_path"]
LOG_DATE = ""
log = Log()
log.PATH = LOG_PATH
logger = log.stream_logger("main")


# db settings
db_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "database": config["database"]["name"],
                "host": config["database"]["db"],
                "password": config["database"]["password"],
                "port": config["database"]["port"],
                "user": config["database"]["user"],
            },
        }
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "apps.resources.regions.models",
                "apps.resources.zones.models",
            ],
            "default_connection": "default",
        }
    },
}


# email settings
EMAIL_AUTH_HOST = config["email"]["auth_host"]
EMAIL_PORT = config["email"]["port"]
EMAIL_USER = config["email"]["user"]
EMAIL_PASS = config["email"]["password"]
ADMIN_EMAIL = config["email"]["admin_email"]

# consul
CONSUL_HOST = config["consul"]["host"]
CONSUL_PORT = config["consul"]["port"]
