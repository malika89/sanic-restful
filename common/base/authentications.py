#!/usr/bin/env python


from sanic_auth import Auth, User
from sanic import exceptions
from common.internal import sso


class SSOAuthentication(Auth):

    DEBUG = False

    def authenticate(self, request):
        token = request.headers.get("sso_token")
        if not token:
            raise exceptions.AuthenticationFailed('请先登入')

        token = request.COOKIES.get('sso_token')

        api = sso.SSO("url", token)
        data = {
            'method': request.method,
            'uri': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'system': 'Domain',
        }
        result = api.auth(**data)
        if not result.OK:
            raise exceptions.AuthenticationFailed('SSO程序或网路异常')

        if result.data.get('code') != 200:
            raise exceptions.AuthenticationFailed(result.data.get('message'))

        user_info = result.data.get('data')

        username = user_info.get('username').lower()
        email = user_info.get('email').lower()
        request.ctx.username = username
        request.ctx.email = email

        return request
