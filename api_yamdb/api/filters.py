from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):

    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year')
