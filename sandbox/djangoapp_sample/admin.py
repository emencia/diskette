from django.contrib import admin

from ..models import Article, Blog, Category


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass
