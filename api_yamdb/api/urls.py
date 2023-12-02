from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIGetToken, APISignup, UsersViewSet,
    TitleViewSet, GenreViewSet, CategoryViewSet,
    ReviewViewSet, CommentViewSet,
)


router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentViewSet, basename='comment')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='review')

urlpatterns = [
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
]
