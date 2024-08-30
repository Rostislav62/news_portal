from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    # Модель для хранения информации об авторах.
    # Каждый автор связан с пользователем (User) и имеет рейтинг.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Метод для обновления рейтинга автора.
        # Рейтинг рассчитывается как:
        # - Суммарный рейтинг всех статей автора, умноженный на 3.
        # - Суммарный рейтинг всех комментариев автора.
        # - Суммарный рейтинг всех комментариев к статьям автора.
        post_ratings = self.post_set.all().aggregate(total_rating=models.Sum('rating'))
        comment_ratings = self.user.comment_set.all().aggregate(total_rating=models.Sum('rating'))
        post_comment_ratings = self.post_set.all().aggregate(total_rating=models.Sum('comment__rating'))

        self.rating = (post_ratings['total_rating'] or 0) * 3 + \
                      (comment_ratings['total_rating'] or 0) + \
                      (post_comment_ratings['total_rating'] or 0)
        self.save()


class Category(models.Model):
    # Модель для хранения категорий новостей/статей.
    # Каждая категория имеет уникальное название.
    name = models.CharField(max_length=255, unique=True)


class Post(models.Model):
    # Модель для хранения постов (статей и новостей).
    # Посты могут иметь одну или несколько категорий и связаны с автором.
    POST_TYPE_CHOICES = [
        ('article', 'Article'),
        ('news', 'News'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        # Метод для увеличения рейтинга поста на единицу.
        self.rating += 1
        self.save()

    def dislike(self):
        # Метод для уменьшения рейтинга поста на единицу.
        self.rating -= 1
        self.save()

    def preview(self):
        # Метод для получения предварительного просмотра текста поста.
        # Возвращает первые 124 символа текста с добавлением многоточия в конце, если текст длиннее.
        return self.text[:124] + '...' if len(self.text) > 124 else self.text


class PostCategory(models.Model):
    # Промежуточная модель для связи многие ко многим между постами и категориями.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    # Модель для хранения комментариев к постам.
    # Комментарии связаны с постами и пользователями.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        # Метод для увеличения рейтинга комментария на единицу.
        self.rating += 1
        self.save()

    def dislike(self):
        # Метод для уменьшения рейтинга комментария на единицу.
        self.rating -= 1
        self.save()
