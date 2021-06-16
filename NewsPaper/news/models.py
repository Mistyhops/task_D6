from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    author_rating = models.IntegerField(default=0)

    def update_rating(self):
        author_post_list = Post.objects.filter(author=self.id)
        post_rating = sum([n.post_rating * 3 for n in author_post_list])
        comment_rating = sum([n.comment_rating for n in Comment.objects.filter(comment_author=self.id)])
        post_comment_rating = sum([n.comment_rating for n in Comment.objects.filter(post__in=author_post_list)])
        self.author_rating = post_rating + comment_rating + post_comment_rating
        print(self.author_rating)
        self.save()

    def __str__(self):
        return f"{self.author.username}"


class Category(models.Model):
    name_category = models.CharField(max_length=100, unique=True)
    subscriber = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.name_category}"


class Post(models.Model):
    article = 'AR'
    news = 'NE'

    CHOICES = [
        (article, 'Статья'),
        (news, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=CHOICES, default=news)
    time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    header = models.CharField(max_length=500)
    text = models.TextField()
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...'

    def get_absolute_url(self):
        return f'/news/{self.id}'

    def __str__(self):
        return f"{self.header}"


class PostCategory(models.Model):
    """Intermediate model for m2m relation between Post and Category models"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post.id}, {self.category.name_category}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

    def __str__(self):
        return f"{self.post.id}, {self.comment_author.username}, {self.text}"
