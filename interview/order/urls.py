
from django.urls import path
from interview.order.views import (
    OrderListCreateView,
    OrderTagListCreateView,
    DeactivateOrderView,
    OrderListByDateView,
    OrderTagsListView,
)


urlpatterns = [
    path('tags/', OrderTagListCreateView.as_view(), name='order-detail'),
    path('', OrderListCreateView.as_view(), name='order-list'),
    path('<int:pk>/deactivate/', DeactivateOrderView.as_view(), name='order-deactivate'),
    path('by-date/', OrderListByDateView.as_view(), name='order-list-by-date'),
    path('<int:pk>/tags/', OrderTagsListView.as_view(), name='order-tags'),
]