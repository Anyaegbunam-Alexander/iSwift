from rest_framework.pagination import PageNumberPagination as DRF_PageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DRF_PageNumberPagination):
    """Default pagination class to be used for pagination
    across entire project."""

    page_size = 10

    def get_paginated_response(self, data):
        return Response(
            {
                "object": "list",
                "count": self.page.paginator.count,
                "current_page": self.page.number,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )
