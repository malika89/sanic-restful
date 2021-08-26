#!/usr/bin/env python

from rest_framework.views import exception_handler

def handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        data = {
            'code': response.status_code,
            'message': response.data['detail']
        }
        response.status_code = 200
        response.data = data

    return response
