from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Пагинация для списка объектов."""

    page_size_query_param = 'limit'
    page_size = 6
