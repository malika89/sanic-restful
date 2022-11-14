#!/usr/bin/env python


"""
authentication func ,here can be replaced by api gateway

suggection solution:pycasbin
"""


import sys

sys.path.append('../../')



class SSO():

    def __init__(self, host, token):
        super().__init__()
        self.host = host
        self.token = token
        self.header = {
            'Content-Type': 'application/json',
            'Cookie': f'sso_token={token}',
        }

    def auth(self, **kwargs):
        pass

