#!/usr/bin/env python


from sanic_auth import Auth, User
from sanic import exceptions
from common.internal import sso


class SSOAuthentication(Auth):

    DEBUG = False

    def authenticate(self, request):
        if request.action in request.no_auth_action or self.DEBUG:
            user = None
            user.sso = {
                'username': 'Anonymous',
                'email': 'anonymous@88tech.net',
                'roleename': 'Anonymous',
            }
            return user, None

        if not request.COOKIES.get('sso_token'):
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

        try:
            user = User.objects.get(username=username)
            if user_info.get('roleename') == 'product':
                user_info['roleename'] = user_info['roleename'].upper()
        except User.DoesNotExist:
            User.objects.update_or_create(username=username, email=email)
            user = User.objects.get(username=username)
        except Exception:
            raise exceptions.AuthenticationFailed('认证异常，请洽管理员')
        setattr(user, 'sso', user_info)
        return user, None
