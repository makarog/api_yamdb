from rest_framework import viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Title, Genre, Category
from .serializers import (
    TitleSerializer,
    GenreSerializer,
    CategorySerializer,
)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    #todo permission_classes = [Administrator]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genres__slug', 'name', 'year')


class GenreViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # todo permission_classes = [Administrator]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # todo permission_classes = [Administrator]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)
