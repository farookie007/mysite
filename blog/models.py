from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


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
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    class Status(models.TextChoices):
        DRAFT = ("DF", "Draft")
        PUBLISHED = ("PB", "Published")

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )
    objects = models.Manager()  # the default manager
    published = PublishedManager()  # our custom manager
    draft = DraftManager()  # for drafted posts

    def __str__(self):
        """String representation for the Post model."""
        return self.title

    def get_absolute_url(self):
        """Returns the url for a particular post using its id"""
        return reverse(
            "blog:post_detail",
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug,
            ],
        )
