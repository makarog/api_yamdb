import datetime as dt
from typing import Any
from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('name', 'year',
                  'description', 'genres', 'category',
                  'rating')

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
        model = Category
        fields = ('name', 'slug')


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки запросов к модели User."""
    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator()
        ]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')

    def validate_role(self, value: str) -> str:
        """Проверяет, имеет ли текущий пользователь право назначать роли."""
        user: User = self.context['request'].user
        if user.is_staff or user.is_admin:
            return value
        raise serializers.ValidationError(
            'Назначать роль может только администратор.'
        )


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для подтверждения токенов пользователя."""
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""
    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator()
        ]
    )
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def create(self, validated_data: dict[str, Any]) -> User:
        """Создает нового пользователя на основе переданных данных."""
        try:
            user, _ = User.objects.get_or_create(
                username=validated_data.get('username'),
                email=validated_data.get('email'),
            )
        except IntegrityError as error:
            raise serializers.ValidationError(
                'Такое имя пользователя уже существует.'
                if 'username' in str(error)
                else 'Пользователь с таким электронным адресом уже существует.'
            )
        return user

    def validate_username(self, value: str) -> str:
        """Проверка имени пользователя на недопустимые значения."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" недопустимо.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('author', 'title')


    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data
        user = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'review')
