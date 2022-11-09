#!/usr/bin/env python


from sanic import exceptions
from sanic_auth import Auth

from common.internal import sso


class SSOAuthentication(Auth):

    DEBUG = False

    def authenticate(self, request):
        token = request.headers.get("sso_token")
        if not token:
            raise exceptions.AuthenticationFailed("please login in first")

        token = request.COOKIES.get("sso_token")

        api = sso.SSO("url", token)
        data = {
            "method": request.method,
            "uri": request.path,
            "user_agent": request.META.get("HTTP_USER_AGENT"),
            "system": "Domain",
        }
        result = api.auth(**data)
        if not result.OK:
            raise exceptions.AuthenticationFailed("auth failed")

        if result.data.get("code") != 200:
            raise exceptions.AuthenticationFailed(result.data.get("message"))

        user_info = result.data.get("data")

        username = user_info.get("username").lower()
        email = user_info.get("email").lower()
        request.ctx.username = username
        request.ctx.email = email

        return request
