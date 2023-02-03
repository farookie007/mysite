from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """
    Model manager for published posts.
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class DraftManager(models.Manager):
    """
    Model manager for posts that are only drafted but not posted yet.
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.DRAFT)


class Post(models.Model):
    """
    Database model for the every Post by a user.
    """

    class Meta:
        ordering = [
            "-publish",
        ]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    class Status(models.TextChoices):
        DRAFT = ("DF", "Draft")
        PUBLISHED = ("PB", "Published")

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )
    objects = models.Manager()  # the default manager
    published = PublishedManager()  # our custom manager
    draft = DraftManager()  # for drafted posts
    tags = TaggableManager()  # for tags

    def __str__(self):
        """String representation for the Post model."""
        return self.title

    def get_absolute_url(self):
        """Returns the absolute url for a particular post using its
        url parameters"""
        return reverse(
            "blog:post_detail",
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug,
            ],
        )


class Comment(models.Model):
    """
    This model represents how the comment by each user is stored
    in the database.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    class Meta:
        ordering = [
            "-created",
        ]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        """String representation for the Comment model."""
        return f"Comment by {self.name} on {self.post}"
