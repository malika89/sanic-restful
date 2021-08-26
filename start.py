#!/usr/bin/python
# coding:utf-8

from sanic import Sanic
from tortoise.contrib.sanic import register_tortoise

from settings import config,db_config
from common.logger import Log
from router import api


app = Sanic(__name__)
app.update_config(config)
app.blueprint(api)

# 注册orm
register_tortoise(app, config=db_config, generate_schemas=True)

@app.listener('before_server_start')
async def before_server_start(app, loop):
    Log.info("before server start")


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    Log.info("before server stop ")


@app.listener('before_server_start')
async def after_server_start(app, loop):
    Log.info("after_server_start")


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    Log.info("after_server_stop")


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8001)