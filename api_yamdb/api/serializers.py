import datetime as dt

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Title, Genre, Category


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = ('name', 'year',
                  'description', 'genres', 'category')

    def validate_year(self, value):
        current_year = dt.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего'
            )
        return value


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
