from django.contrib import admin

from .models import User, Category, Comment, Genre, Review, Title, TitleGenre


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
admin.site.register(TitleGenre)
