from django_filters import FilterSet
from django.forms import DateInput, SelectMultiple
import django_filters

from .models import Post, Category


class PostFilter(FilterSet):
    time = django_filters.DateTimeFilter(field_name='time', widget=DateInput(attrs={'type':'date'}),
                                         lookup_expr='gt', label='Позже даты')
    header = django_filters.CharFilter(field_name='header',
                                       lookup_expr='icontains',
                                       label='Заголовок')
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all(), widget=SelectMultiple())

    class Meta:
        model = Post
        fields = {
            'author':['exact'],
        }
