#!/usr/bin/python
# coding:utf-8

from json import dumps as json_dumps
from collections import OrderedDict
import functools
import inspect
from math import ceil
from sanic import HTTPResponse

from libs.encoder import CJsonEncoder


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


class Paginator:
    # Translators: String used to replace omitted page numbers in elided page
    # range generated by paginators, e.g. [1, 2, '…', 5, 6, 7, '…', 9, 10].
    ELLIPSIS = ('…')

    def __init__(self, object_list, per_page, orphans=0,
                 allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(('That page number is not an integer'))
        if number < 1:
            raise EmptyPage(('That page number is less than 1'))
        if number > self.num_pages():
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise InvalidPage(('That page contains no results'))
        return number

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count():
            top = self.count()
        return self.object_list[bottom:top], number

    def count(self):
        """Return the total number of objects, across all pages."""
        c = getattr(self.object_list, 'count', None)
        if callable(c) and not inspect.isbuiltin(c) and method_has_no_args(c):
            return c()
        return len(list(self.object_list))

    def num_pages(self):
        """Return the total number of pages."""
        if self.count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self.count() - self.orphans)
        return ceil(hits / self.per_page)


class PageNumberPagination():
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    http://api.example.org/accounts/?page=4
    http://api.example.org/accounts/?page=4&page_size=100
    """
    # The default page size.
    page_size = 20
    paginator_class = Paginator
    page_query_param = 'page'
    page_size_query_param = None
    max_page_size = None
    last_page_strings = ('last',)
    invalid_page_message = ('Invalid page.')

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            queryset, num = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise Exception(msg)
        self.request = request
        return list(queryset)

    def get_page_number(self, request, paginator):
        page_number = dict(request.query_args).get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages()
        return page_number

    def get_paginated_response(self, data):
        return HTTPResponse(json_dumps(OrderedDict([
            ('count', len(data)),
            ('results', data),
        ]), **{"cls": CJsonEncoder}))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    dict(request.query_args)[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size


def method_has_no_args(meth):
    """Return True if a method only accepts 'self'."""
    count = len([
        p for p in _get_callable_parameters(meth)
        if p.kind == p.POSITIONAL_OR_KEYWORD
    ])
    return count == 0 if inspect.ismethod(meth) else count == 1


def _get_callable_parameters(meth_or_func):
    is_method = inspect.ismethod(meth_or_func)
    func = meth_or_func.__func__ if is_method else meth_or_func
    return _get_func_parameters(func, remove_first=is_method)


@functools.lru_cache(maxsize=512)
def _get_func_parameters(func, remove_first):
    parameters = tuple(inspect.signature(func).parameters.values())
    if remove_first:
        parameters = parameters[1:]
    return parameters


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret
