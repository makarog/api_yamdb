from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserRegistrationView, UserTokenView, UserViewSet,
    TitleViewSet, GenreViewSet, CategoryViewSet,
)


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/auth/signup/',
        UserRegistrationView.as_view(),
        name='registration'
    ),
    path(
        'v1/auth/token/',
        UserTokenView.as_view(),
        name='token'
    ),
]
