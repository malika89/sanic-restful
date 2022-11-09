#!/usr/bin/python

# action 函数，用于支持自定义方法(action decorator for custom func/route)

import inspect


def get_extra_actions(cls):
    """
    Get the methods that are marked as an extra ViewSet `@action`.
    """
    return [
        _check_attr_name(method, name)
        for name, method in inspect.getmembers(cls, _is_extra_action)
    ]


def action(methods=None, detail=None, url_path=None, url_name=None, **kwargs):
    """
    reference django actions
    """
    methods = ["get"] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    assert detail is not None, "@action() missing required argument: 'detail'"

    # name and suffix are mutually exclusive
    if "name" in kwargs and "suffix" in kwargs:
        raise TypeError(
            "`name` and `suffix` are mutually exclusive arguments."
        )

    def decorator(func):
        func.mapping = MethodMapper(func, methods)

        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.url_name = (
            url_name if url_name else func.__name__.replace("_", "-")
        )

        func.kwargs = kwargs

        # Set descriptive arguments for viewsets
        if "name" not in kwargs and "suffix" not in kwargs:
            func.kwargs["name"] = pretty_name(func.__name__)
        func.kwargs["description"] = func.__doc__ or None

        return func

    return decorator


def _is_extra_action(attr):
    return hasattr(attr, "mapping") and isinstance(attr.mapping, MethodMapper)


def is_custom_action(action):
    return action not in {"retrieve", "list", "post", "put", "patch", "delete"}


def _check_attr_name(func, name):
    assert func.__name__ == name, (
        "Expected function (`{func.__name__}`) to match its attribute name "
        "(`{name}`). If using a decorator, ensure the inner function is "
        "decorated with `functools.wraps`, or that `{func.__name__}.__name__` "
        "is otherwise set to `{name}`."
    ).format(func=func, name=name)
    return func


def pretty_name(name):
    """Convert 'first_name' to 'First name'."""
    if not name:
        return ""
    return name.replace("_", " ").capitalize()


class MethodMapper(dict):
    """
    Enables mapping HTTP methods to different ViewSet methods for a single,
    logical action.

    Example usage:

        class MyViewSet(ViewSet):

            @action(detail=False)
            def example(self, request, **kwargs):
                ...

            @example.mapping.post
            def create_example(self, request, **kwargs):
                ...
    """

    def __init__(self, action, methods):
        self.action = action
        for method in methods:
            self[method] = self.action.__name__

    def _map(self, method, func):
        assert (
            method not in self
        ), "Method '{}' has already been mapped to '.{}'.".format(
            method, self[method]
        )
        assert func.__name__ != self.action.__name__, (
            "Method mapping does not behave like the property decorator. You "
            "cannot use the same method name for each mapping declaration."
        )

        self[method] = func.__name__

        return func

    def get(self, func):
        return self._map("get", func)

    def post(self, func):
        return self._map("post", func)

    def put(self, func):
        return self._map("put", func)

    def patch(self, func):
        return self._map("patch", func)

    def delete(self, func):
        return self._map("delete", func)

    def head(self, func):
        return self._map("head", func)

    def options(self, func):
        return self._map("options", func)

    def trace(self, func):
        return self._map("trace", func)
