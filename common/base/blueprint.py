#!/usr/bin/python


"""
blueprint 添加自动详情功能以及支持action动作
 :using blueprint to add common route automatically，eg: detail
 :with action decorator support custom method func

"""
from collections.abc import Iterable

from sanic.blueprints import Blueprint


class BaseBlueprint(Blueprint):
    def __init__(
        self,
        name=None,
        url_prefix=None,
        host=None,
        version=None,
        strict_slashes=None,
        version_prefix="/v",
    ):
        super().__init__(
            name, url_prefix, host, version, strict_slashes, version_prefix
        )

    def add_routes(
        self,
        handler,
        uri: str,
        methods: Iterable[str] = frozenset({"GET"}),
        host=None,
        strict_slashes=None,
        version=None,
        name=None,
        stream=False,
        version_prefix="/v",
    ):
        """
        overwrite and bulk add_router
        router.add_route(Books.as_view(),'/')
        router.add_route(Books.as_view(),'/<pk:int>')
        router.add_route(Books.as_view(),'/<action:string>')
        router.add_route(Books.as_view(),'/<pk:int>/<action:string>')
        """
        if hasattr(handler, "custom_actions"):
            methods_ = handler.custom_actions
            for method_ in methods_:
                action_methods = list(method_.mapping.keys())
                self.add_route(
                    handler,
                    uri=f"{uri}<action:string>"
                    if not method_.detail
                    else f"{uri}/<pk:int>/<action:string>",
                    methods=action_methods,
                    host=host,
                    strict_slashes=strict_slashes,
                    stream=stream,
                    version=version,
                    name=name,
                    version_prefix=version_prefix,
                )
        # 原来router
        self.add_route(
            handler,
            uri,
            methods=methods,
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            version_prefix=version_prefix,
        )
        # detail router
        self.add_route(
            handler,
            f"{uri}<pk:int>",
            methods=methods,
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            version_prefix=version_prefix,
        )
