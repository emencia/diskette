from sandbox.djangoapp_sample.factories import (
    ArticleFactory, BlogFactory, CategoryFactory
)
from sandbox.djangoapp_sample.models import Blog


def test_blog_creation(db):
    """
    Factory should correctly create a new Blog object without any errors
    """
    blog = BlogFactory(title="foo")
    assert blog.title == "foo"


def test_category_creation(db):
    """
    Factory should correctly create a new Blog object without any errors
    """
    category = CategoryFactory(title="foo")
    assert category.title == "foo"


def test_article_creation(db):
    """
    Factory should correctly create a new Article object without any errors
    """
    article = ArticleFactory(title="foo")

    assert article.title == "foo"
    assert isinstance(article.blog, Blog) is True
