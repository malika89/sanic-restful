#!/usr/bin/python

import boto3

from common.external.common_ecs import *

class Client(ClientBase):
    def __init__(self,access_key,secret_key,region=""):
        self.client = boto3.client("ec2",aws_access_key_id=access_key,aws_secret_access_key=secret_key,
                                   use_ssl=False,region_name=region)
        self.security_group_rule = SecurityGroupRule(self.client)

class SecurityGroupRule(SecurityGroupRuleBase):

    def create(self,**kwargs):
        try:
            if kwargs.get("direct", "") == "out":
                data = self.client.authorize_security_group_ingress(
                    GroupId=kwargs["security_group_id"],
                    IpPermissions=kwargs["rule"])
            else:
                data = self.client.authorize_security_group_egress(
                    GroupId=kwargs["security_group_id"],
                    IpPermissions=kwargs["rule"])
        except Exception as e:
            return self.format_response(err=e)
        return self.format_response(data)
