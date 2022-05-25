from django.urls import path
from . import views
from . import dashboard_data

app_name = "blog"
urlpatterns = [
    path("", views.BlogListView.as_view(), name="list"),
    path("data/", dashboard_data.dashboard_charts_data, name="charts-data"),
    path("details/<int:pk>/", views.BlogDetailView.as_view(), name="details"),
    path("search/", views.BlogSearchView.as_view(), name="search"),
    path("dashboard/", views.BlogDashboardView.as_view(), name="dashboard"),
    path("dashboard/posts/", views.BlogDashboardPostsListView.as_view(), name="dashboard_posts"),
    path("dashboard/editpost/<int:pk>/", views.BlogUpdateView.as_view(), name="edit"),
    path("dashboard/addpost/", views.BlogCreateView.as_view(), name="add"),
    path("dashboard/search/", views.BlogDashboardSearchView.as_view(), name="dashboard_search"),
    path("dashboard/profile/<int:pk>/", views.BloggerUpdateView.as_view(), name="profile"),
]
