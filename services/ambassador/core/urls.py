from django.urls import path

from .views import (
    ProductFrontendAPIView, ProductBackendAPIView, LinkAPIView, StatsAPIView, RankingsAPIView,
    UserAPIView, RegisterAPIView, LoginAPIView, LogoutAPIView, ProfileInfoAPIView, ProfilePasswordAPIView
)

urlpatterns = [
    path('products/frontend', ProductFrontendAPIView.as_view()),
    path('products/backend', ProductBackendAPIView.as_view()),
    path('links', LinkAPIView.as_view()),
    path('stats', StatsAPIView.as_view()),
    path('rankings', RankingsAPIView.as_view()),

    # user urls
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('users/info', ProfileInfoAPIView.as_view()),
    path('users/password', ProfilePasswordAPIView.as_view()),
]
