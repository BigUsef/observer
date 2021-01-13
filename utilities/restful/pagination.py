from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination as RestPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(RestPageNumberPagination):
    """
    Custom class to override DRF PageNumberPagination
    this class override response of all list to contain
    Response:
    {
        'next': next pagination link,
        'previous': previous pagination link,
        'count': cont of all object in list,
        'pages': total pages count,
        'current': current page size,
        'result': the data of list,
        'status: flag to get status of response
    }
    """

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('count', self.page.paginator.count),
            ('pages', self.page.paginator.num_pages),
            ('current', self.page.number),
            ('result', data),
            ('status', True),
        ]))
