import datetime as dt

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .constants import CONST_FOR_LENGTH

User = get_user_model()


class BaseModel(models.Model):
    name = models.CharField(max_length=CONST_FOR_LENGTH)
    slug = models.SlugField(unique=True, max_length=50, allow_unicode=False)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(BaseModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseModel):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=CONST_FOR_LENGTH, verbose_name='Название')
    year = models.PositiveSmallIntegerField(verbose_name='Год выпуска', db_index=True)
    description = models.TextField(verbose_name='Описание', blank=False)
    genre = models.ManyToManyField(
        Genre,
        related_name='genre',
        verbose_name='Жанры'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories',
        verbose_name='Категория'
    )

    def __str__(self):
        return self.name

    def clean(self):
        """Проверяем на корректность ввода года выпуска."""
        current_year = dt.date.today().year
        if self.year > current_year:
            raise ValidationError('Год выпуска не может быть больше текущего')


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)
        unique_together = ('author', 'title')


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)
