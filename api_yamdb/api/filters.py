import django_filters

from reviews.models import Title


class TitleFilterSet(django_filters.FilterSet):
    genre = django_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Title
        fields = '__all__'
