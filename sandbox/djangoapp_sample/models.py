from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def safe_get_user_model():
    """
    Safe loading of the User model, customized or not.
    """
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    return apps.get_registered_model(user_app, user_model)


class Blog(models.Model):
    """
    A very simple blog to contain articles.

    Attributes:
        title (models.CharField): Required unique title string.
    """
    title = models.CharField(
        _("title"),
        max_length=55,
        default="",
        unique=True,
    )

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ["title"]

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    A very simple category to relate from articles.

    Attributes:
        title (models.CharField): Required unique title string.
    """
    title = models.CharField(
        _("title"),
        max_length=55,
        default="",
        unique=True,
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["title"]

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    A simple article for a Blog.

    Attributes:
        blog (models.ForeignKey): Required related Blog object.
        title (models.CharField): Required title string.
        content (models.TextField): Optionnal text content.
        categories (models.ManyToManyField): Related categories.
        publish_start (models.DateTimeField): Required publication date determine
            when article will be available.
    """
    blog = models.ForeignKey(
        Blog,
        verbose_name="Related blog",
        on_delete=models.CASCADE
    )

    categories = models.ManyToManyField(
        Category,
        verbose_name=_("categories"),
        blank=True,
    )

    author = models.ForeignKey(
        safe_get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        _("title"),
        max_length=150,
        default="",
    )

    content = models.TextField(
        _("content"),
        blank=True,
        default="",
    )

    publish_start = models.DateTimeField(
        _("publication start"),
        db_index=True,
        default=timezone.now,
    )

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-publish_start"]

    def __str__(self):
        return self.title
