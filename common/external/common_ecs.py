#!/usr/bin/python

"""
基类资源操作
"""
class ClientBase:
    def __init__(self,access_key,secret_key,region=""):
        self.client = None
        self.vpc = VPCBase(self.client)
        self.route =None
        self.eip =None
        self.nat = None
        self.instance = InstanceBase(self.client)
        self.security_group = SecurityGroupBase(self.client)
        self.security_group_rule = SecurityGroupRuleBase(self.client)
        # 基础资源
        self.region = Region(self.client)
        self.zone = Zone(self.client)
        self.image = Image(self.client)

class CommonRequest():
    # endpoint 为资源操作入口，transfer为数据转换器
    # example {"endpoint":"describe_instance","source":"a.c.d","map":{"Region":"region","Network":"resouces"}}
    list_endpoint = {"endpoint": "", "source":""}
    create_endpoint = {"endpoint": ""}
    update_endpoint= ""
    delete_endpoint = ""

    def __init__(self,client):
        self.client = client

    def format_response(self,data,err=False):
        response = {"code":200,"message":"success","data":data}
        if err:
            response.update({"code":400,"message":err,"data":[]})
        return response


    @staticmethod
    def walk_node(data,node):
        if not data or not node:
            return data
        trees = node.split('.')
        for tree in trees:
            data = data.get(tree,"")
            if not data:
                break
        return data


    def list(self,**kwargs):
        func = getattr(self.client,self.list_endpoint["endpoint"])
        res = func(**kwargs)
        # 请求后数据所在节点
        node=self.list_endpoint.get("source","")
        data = res if node  else self.walk_node(res,node)

        # 字段转换
        transfer_map = self.list_endpoint.get("map","")
        if transfer_map:
            for k,v in transfer_map.items():
                data[v] = data.get(k,"")
        return self.format_response(data)

    def create(self,**kwargs):
        func = getattr(self.client,self.list_endpoint["endpoint"])
        try:
            res = func(**kwargs)
        except Exception as e:
            return self.format_response([],e)
        node=self.list_endpoint.get("source","")
        data = res if node  else self.walk_node(res,node)
        return self.format_response(data)

    def update(self,**kwargs):
        func = getattr(self.client,self.list_endpoint)
        try:
            res = func(**kwargs)
        except Exception as e:
            return self.format_response([],e)
        return self.format_response(res)

    def delete(self,resource_id):
        func = getattr(self.client,self.list_endpoint)
        try:
            res = func(resource_id)
        except Exception as e:
            return self.format_response([],e)
        return self.format_response(res)


class VPCBase(CommonRequest):
    list_endpoint = {"endpoint": "", "source":""}
    create_endpoint = {"endpoint": ""}
    update_endpoint= ""
    delete_endpoint = ""

class InstanceBase(CommonRequest):
    list_endpoint = {"endpoint": "describe_instances", "source":""}
    create_endpoint = {"endpoint": ""}
    update_endpoint= ""
    delete_endpoint = ""

    def start(self,instance_id):
        try:
            self.client.start_instances(InstanceIds=[instance_id], DryRun=True)
        except Exception as e:
            if 'DryRunOperation' not in str(e):
                return self.format_response(err=e)
        try:
            response = self.client.start_instances(InstanceIds=[instance_id], DryRun=False)
        except Exception as e:
            return self.format_response(err=e)
        return self.format_response(data=response)

    def stop(self, instance_id):
        try:
            self.client.stop_instances(InstanceIds=[instance_id], DryRun=True)
        except Exception as e:
            if 'DryRunOperation' not in str(e):
                return self.format_response(err=e)
        try:
            response = self.client.stop_instances(InstanceIds=[instance_id], DryRun=False)
        except Exception as e:
            return self.format_response(err=e)
        return self.format_response(data=response)

    def restart(self, instance_id):
        try:
            self.client.reboot_instances(InstanceIds=['INSTANCE_ID'], DryRun=True)
        except Exception as e:
            if 'DryRunOperation' not in str(e):
                return self.format_response(err=e)
                print("You don't have permission to reboot instances.")
        try:
            response = self.client.reboot_instances(InstanceIds=['INSTANCE_ID'], DryRun=False)
        except Exception as e:
            return self.format_response(err=e)
        return self.format_response(data=response)


class SecurityGroupBase(CommonRequest):
    list_endpoint = {"endpoint": "describe_security_groups", "source":""}
    create_endpoint = {"endpoint": ""}
    update_endpoint= ""
    delete_endpoint = "delete_security_group"


class SecurityGroupRuleBase(CommonRequest):
    list_endpoint = {"endpoint": "describe_security_group_ingress", "source":""}
    create_endpoint = {"endpoint": "authorize_security_group_ingress"}
    delete_endpoint = "delete_security_group_ingress"


#################
# readonly  基础资源，从后台获取同步
#################
class Region(CommonRequest):
    list_endpoint = {"endpoint": "describe_regions", "source":""}


class Zone(CommonRequest):
    list_endpoint = {"endpoint": "describe_availability_zones", "source":""}


class Image(CommonRequest):
    list_endpoint = {"endpoint": "describe_regions", "source":""}
