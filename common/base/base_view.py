#!/usr/bin/python

import operator
import time
from datetime import datetime
from functools import reduce

from sanic import response
from sanic.exceptions import NotFound
from sanic.log import logger
from sanic.views import HTTPMethodView
from tortoise.queryset import Q, QuerySet

from common.base.authentications import SSOAuthentication
from common.base.base_model import BaseModel
from common.base.pagenation import PageNumberPagination
from libs.action import action, get_extra_actions


class BaseView(HTTPMethodView):
    # 身份认证
    auth_classes = (SSOAuthentication,)

    # 审计
    audit_class = None

    # 模型
    Model = BaseModel

    # 序列化
    serializer_class = None

    # 分页
    pagination_class = PageNumberPagination

    # 不需要身份认证的函数
    no_auth_action = []

    # 显示的字段, 默认全部显示
    display_fields = []

    # 可过滤查询的字段
    # 注: 以下多功能搜索, 都需要先在此设罝
    filter_fields = []

    # 范围查询字段, 时间or数字
    # 方法 /?update_time=2020-01-01,2020-01-05
    range_fields = ["update_time", "create_time"]

    # 可模糊匹配罝字段
    fuzzy_search = []

    # 可多栏搜索的字段
    search_fields = []

    # 上传时，校验的栏位
    upload_required_columns = []

    # choices接口, 返回的数据类型
    choices_option = ["choices", "foregin_key", "submodel", "many2many"]

    # 提供给前端需要批量编辑的字段
    batch_editable = []

    # 默认排序
    ordering = "id"

    def __init__(self, *args, **kwargs):
        self.code = 200
        self.message = None
        self.response_data = None
        self.status = 200
        self.timer = 0
        self.start_time = time.time()
        self.authentication_classes = self.auth_classes

    @classmethod
    def as_view(cls, *class_args, **class_kwargs):
        """Return view function for use with the routing system, that
        dispatches request to appropriate handler method.
        """

        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)
        view.view_class = cls
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__name__ = cls.__name__
        view.custom_actions = get_extra_actions(cls)
        return view

    def init_request(self, request, *args, **kwargs):
        self.perform_authentication(request)
        self.check_permissions(request)

        # 记录操作人&操作時間
        if isinstance(request.data, dict):
            request.data._mutable = True

        if request.method in ["POST"]:
            if isinstance(request.data, list):
                for data in request.data:
                    data["create_by"] = data.get(
                        "create_by", str(request.user.username)
                    )
                    data["update_by"] = data.get(
                        "update_by", str(request.user.username)
                    )
                    data["create_time"] = data.get(
                        "create_time", datetime.now()
                    )
                    data["update_time"] = data.get(
                        "update_time", datetime.now()
                    )
            else:
                data = request.data
                data["create_by"] = request.data.get(
                    "create_by", str(request.user.username)
                )
                data["update_by"] = request.data.get(
                    "update_by", str(request.user.username)
                )
                data["create_time"] = request.data.get(
                    "create_time", datetime.now()
                )
                data["update_time"] = request.data.get(
                    "update_time", datetime.now()
                )
        elif request.method in ["PUT"]:
            request.data["update_by"] = request.data.get(
                "update_by", str(request.user.username)
            )
            request.data["update_time"] = request.data.get(
                "update_time", datetime.now()
            )
        elif request.method in ["DELETE"]:
            request.data["update_by"] = request.data.get(
                "update_by", str(request.user.username)
            )
            request.data["update_time"] = request.data.get(
                "update_time", datetime.now()
            )

        headers, body, info = self.access_log(request)
        self.audit_data = {
            "headers": headers,
            "body": body,
            "info": info,
        }

    @staticmethod
    def record_log(request):
        meta = request._request.META
        remote_ip = meta["REMOTE_ADDR"]
        if "HTTP_X_FORWARDED_FOR" in meta:
            remote_ip = meta["HTTP_X_FORWARDED_FOR"].split(",")[0]

        info = {
            "user": request.user.username,
            "method": request.method,
            "path": request.path,
            "param": meta["QUERY_STRING"],
            "remote_ip": remote_ip,
        }
        headers = request._request.headers
        body = request.data
        logger.info(info)
        logger.info(body)
        return headers, body, info

    # 添加审计
    def audit(self):
        info = self.audit_data["info"]
        headers = self.audit_data["headers"]
        body = self.audit_data["body"]
        data = {
            "code": self.code,
            "message": self.message,
            "time": self.timer,
        }
        try:
            audit = self.audit_class()
            audit.create(
                self.request,
                info=info,
                headers=headers,
                body=body,
                response=data,
            )
        except Exception as e:
            logger.exception("审计错误")

    # 权限
    def check_permission(self, request, *args, **kwargs):
        pass

    def dispatch_request(self, request, *args, **kwargs):
        # 添加错误异常处理
        self.request = request
        try:
            self.init_request(request, *args, **kwargs)
        except Exception as e:
            return response.json(e)
        # 审计、日志
        if self.audit_class:
            self.audit()
        # restful 路由转发
        if kwargs.get("pk", 0) and request.method.lower() == "get":
            return self.retrive(self, request, *args, **kwargs)
        elif kwargs.get("action", "") != "":
            handler = getattr(self, kwargs["action"], None)
            if request.method.lower() not in handler.mapping.keys():
                return response.json(
                    {"code": 400, "message": "Wrong Method: not supported"}
                )
        else:
            handler = getattr(self, request.method.lower(), None)
        # 添加restful 路由分发
        return handler(request, *args, **kwargs)

    def retrive(self, request, *args, **kwargs):
        return response.json({"code": 200, "message": "get one"})

    async def get(self, request, *args, **kwargs):
        self.queryset = self.Model.all()
        queryset = await self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            # serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(page)
        return response.json({"code": 200, "message": "get success"})

    # You can also use async syntax
    async def post(self, request, *args, **kwargs):
        return response.json({"code": 200, "message": "success"})

    async def put(self, request, *args, **kwargs):
        return response.json({"code": 200, "message": "success"})

    async def patch(self, request, *args, **kwargs):
        return response.json({"code": 200, "message": "success"})

    async def delete(self, request, *args, **kwargs):
        return response.json({"code": 200, "message": "success"})

    @action(detail=False)
    async def choices(self, request, *args, **kwargs):
        return response.json({"code": 200, "message": "choices"})

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        try:
            obj = queryset.get(**filter_kwargs)
        except queryset.model.DoesNotExist:
            raise NotFound(
                "No %s matches the given query."
                % queryset.model._meta.object_name
            )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instances that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }

    def filter_queryset(self, queryset):
        search_fields = self.get_search_fields(self, self.request)
        search_terms = self.get_search_terms(self.request)

        if not search_fields or not search_terms:
            return queryset.filter().values()

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]
        conditions = []
        for search_term in search_terms:
            queries = [
                Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        queryset = (
            queryset.filter(reduce(operator.and_, conditions))
            .distinct()
            .values()
        )
        return queryset

    @property
    def paginator(self):
        """
        The paginator instances associated with the view, or `None`.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset, self.request, view=self
        )

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, "search_fields", None)

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = dict(request.query_args).get("search", "")
        params = params.replace("\x00", "")  # strip null characters
        params = params.replace(",", " ")
        return params.split()

    def construct_search(self, field_name):

        lookup_prefixes = {
            "^": "istartswith",
            "=": "iexact",
            "@": "search",
            "$": "iregex",
        }
        lookup = lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = "icontains"
        return "__".join([field_name, lookup])
