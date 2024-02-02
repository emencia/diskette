import factory

from django.utils import timezone

from ..models import Article, Blog, Category


class BlogFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Blog.
    """
    title = factory.Sequence(lambda n: "Blog {0}".format(n))

    class Meta:
        model = Blog


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Blog.
    """
    title = factory.Sequence(lambda n: "Category {0}".format(n))

    class Meta:
        model = Category


class ArticleFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of an Article.
    """
    blog = factory.SubFactory(BlogFactory)
    title = factory.Sequence(lambda n: "Article {0}".format(n))
    content = factory.Faker("text", max_nb_chars=150)

    class Meta:
        model = Article

    @factory.lazy_attribute
    def publish_start(self):
        """
        Return current date.

        Returns:
            datetime.datetime: Current time.
        """
        return timezone.now()
