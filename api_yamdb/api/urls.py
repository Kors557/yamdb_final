from django.urls import include, path
from rest_framework import routers
from .views import (
    CategoriesViewSet,
    GenresViewSet,
    TitlesViewSet,
    ReviewViewSet,
    CommentViewSet)
from users.views import UsersViewSet, RegisterUser, TakeToken

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register(r'categories', CategoriesViewSet, basename='categories')
v1_router.register(r'genres', GenresViewSet, basename='genres')
v1_router.register(r'titles', TitlesViewSet, basename='titles')
v1_router.register(r'users', UsersViewSet, basename='users')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', RegisterUser.as_view(), name='register_user'),
    path('v1/auth/token/', TakeToken.as_view(), name='take_token'),
    path('v1/', include(v1_router.urls)),
]
