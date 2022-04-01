from django import forms
from django.forms import SelectMultiple

from folioblog.blog.models import BlogCategory, BlogTag


class TagWidget(SelectMultiple):
    """Due to tagify input text, we need to parse query parameter"""

    def value_from_datadict(self, data, files, name):
        return list(filter(None, data.get(name, '').split(',')))


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False)
    categories = forms.ModelMultipleChoiceField(
        queryset=BlogCategory.objects.all(),
        to_field_name='slug',
        required=False,
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=BlogTag.objects.all(),
        to_field_name='slug',
        required=False,
        widget=TagWidget,
    )
