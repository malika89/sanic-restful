#!/usr/bin/python
# coding:utf-8

from sanic import Sanic
from tortoise.contrib.sanic import register_tortoise

from settings import config,db_config,CONSUL_HOST,CONSUL_PORT
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


def register_consul():
    from libs.consul import Consul
    import consul
    consul_client=Consul(CONSUL_HOST,CONSUL_PORT)

    consul_client.RegisterService(__name__,CONSUL_HOST,CONSUL_PORT)

    check = consul.Check().tcp(CONSUL_HOST,CONSUL_PORT, "5s", "30s", "30s")
    res=consul_client.GetService(__name__)
    Log.info(f'consul注册结果，{res}')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8001)