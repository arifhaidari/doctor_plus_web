import imp
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination



class CustomPagination(PageNumberPagination):  #LimitOffsetPagination
    page_size   =  10 #20
    # default_limit   = 3
    # max_limit       = 10
    #limit_query_param = 'lim' 
    
class ApptListTilePagination(PageNumberPagination):
    page_size   =  6 # 10
    # default_limit   = 8


# class PaginationHandlerMixin(object):
#     @property
#     def paginator(self):
#         if not hasattr(self, '_paginator'):
#             if self.pagination_class is None:
#                 self._paginator = None
#             else:
#                 self._paginator = self.pagination_class()
#         else:
#             pass
#         return self._paginator
#     def paginate_queryset(self, queryset):
        
#         if self.paginator is None:
#             return None
#         return self.paginator.paginate_queryset(queryset, self.request, view=self)
#     def get_paginated_response(self, data):
#         assert self.paginator is not None
#         return self.paginator.get_paginated_response(data)