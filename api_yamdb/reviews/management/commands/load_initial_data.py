import csv

from django.core.management.base import BaseCommand

from reviews.models import Title, Category, Genre, Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Load initial data from CSV files'

    def handle(self, *args, **options):
        # Load Categories
        with open('static/data/category.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                )
        # Load Users
        with open('static/data/users.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                )

        # Load Genres
        with open('static/data/genre.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                )

        # Load Titles
        with open('static/data/titles.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category_id = row['category']
                category = Category.objects.get(id=category_id)

                Title.objects.create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=category,
                )

        with open('static/data/genre_title.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title_id = row['title_id']
                title = Title.objects.get(id=title_id)
                genre_id = row['genre_id']
                genre = Genre.objects.get(id=genre_id)

                title.genre.add(genre)

        # Load Reviews
        with open('static/data/review.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title_id = row['title_id']
                title = Title.objects.get(id=title_id)
                author_id = row['author']
                author = User.objects.get(id=author_id)

                Review.objects.create(
                    id=row['id'],
                    title=title,
                    text=row['text'],
                    author=author,
                    score=row['score'],
                    pub_date=row['pub_date'],
                )

        # Load Comments
        with open('static/data/comments.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                review_id = row['review_id']
                review = Review.objects.get(id=review_id)
                author_id = row['author']
                author = User.objects.get(id=author_id)

                Comment.objects.create(
                    id=row['id'],
                    review=review,
                    text=row['text'],
                    author=author,
                    pub_date=row['pub_date'],
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded initial data'))
