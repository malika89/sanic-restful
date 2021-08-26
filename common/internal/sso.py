#!/usr/bin/env python


import sys
import requests

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

