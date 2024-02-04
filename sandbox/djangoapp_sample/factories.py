import factory

from django.utils import timezone

from sandbox.djangoapp_sample.models import Article, Blog, Category


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
        skip_postgeneration_save = True

    @factory.lazy_attribute
    def publish_start(self):
        """
        Return current date.

        Returns:
            datetime.datetime: Current time.
        """
        return timezone.now()

    @factory.post_generation
    def fill_categories(self, create, extracted, **kwargs):
        """
        Add categories.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If ``True``, will create a new random category
                object. If a list assume it's a list of Category objects to add.
                Else if empty don't do anything.
        """
        # Do nothing for build strategy
        if not create or not extracted:
            return

        # Create a new random category
        if extracted is True:
            categories = [CategoryFactory()]
        # Take given category objects
        else:
            categories = extracted

        # Add categories
        for category in categories:
            self.categories.add(category)
