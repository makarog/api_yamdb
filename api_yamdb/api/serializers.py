import datetime as dt
from typing import Any, Union

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.cache import cache
from django.db.utils import IntegrityError
from rest_framework import serializers, status
from rest_framework.response import Response


from constants import LENGTH_CODE, ADMIN
from reviews.models import Title, Genre, Category
from users.models import User


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


class UserRegistrationSerializer(serializers.ModelSerializer):
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
        fields = (
            'username',
            'email'
        )

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


class UserTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для подтверждения токенов пользователя."""
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )

    def validate(
            self, attrs: dict[str, str]
    ) -> Union[dict[str, str], Response]:
        """
        Проверяет существует пользователь с переданым username.
        Проверяет корректность confirmation_code.
        """
        username: str = attrs.get('username')
        confirmation_code: str = attrs.get('confirmation_code')
        if not User.objects.filter(username=username).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        if (
            len(confirmation_code) != LENGTH_CODE
            and confirmation_code != cache.get(username)
        ):
            raise serializers.ValidationError(
                'Код подтверждения введен неверно.'
            )
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки запросов к модели User."""
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_role(self, value: str) -> str:
        """Проверяет, имеет ли текущий пользователь право назначать роли."""
        user: User = self.context['request'].user
        if user.is_staff or user.role == ADMIN:
            return value
        raise serializers.ValidationError(
            'Назначать роль может только администратор.'
        )
