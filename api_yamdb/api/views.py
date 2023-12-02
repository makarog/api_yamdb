from typing import Any

from django_filters.rest_framework import DjangoFilterBackend

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import generics, viewsets, status, mixins, filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import Token, RefreshToken
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User
from .mixins import AddPermissionsMixin, CreateListDestroySearchViewSet
from .permissions import (
    IsAdminOnly,
    IsAdminObject,
    IsAuthor,
    IsModerator
)

from .serializers import (
    TitleSerializer,
    GenreSerializer,
    CategorySerializer,

    UserRegistrationSerializer,
    UserTokenSerializer,
    UserSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from .utils import send_confirmation_code
from constants import LENGTH_CODE


class TitleViewSet(AddPermissionsMixin, viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genres__slug', 'name', 'year')


class GenreViewSet(CreateListDestroySearchViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)


class CategoryViewSet(CreateListDestroySearchViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)


class UserRegistrationView(generics.CreateAPIView):
    """Представление для регистрации пользователя."""
    serializer_class = UserRegistrationSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Создает пользователя и отправляет код подтверждения
        на указанный адрес электронной почты.
        """
        serializer: dict[str, str] = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()
        confirmation_code: str = get_random_string(length=LENGTH_CODE)
        cache.set(user.username, confirmation_code)
        send_confirmation_code(user.email, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTokenView(generics.CreateAPIView):
    """Получение пользователем JWT-токена."""
    serializer_class = UserTokenSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Обработка POST-запроса на получение JWT-токена."""
        serializer: dict[str, str] = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username: str = request.data['username']
        user: User = get_object_or_404(User, username=username)
        refresh: Token = RefreshToken.for_user(user)
        return Response({'token': str(refresh.access_token)})


class UserViewSet(viewsets.ModelViewSet):
    """ Представление для работы с пользователями в системе."""
    serializer_class = UserSerializer
    queryset = User.objects.order_by('username').all()
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsAdminOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request) -> Response:
        """Получает информацию о текущем пользователе."""
        serializer: UserSerializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def patch_me(self, request: Request) -> Response:
        """Изменяет информацию о текущем пользователе."""
        serializer: UserSerializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return self.get_title().reviews.all()

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        serializer.save(title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return self.get_review().comments.all()

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def perform_create(self, serializer):
        serializer.save(review=self.get_review())
