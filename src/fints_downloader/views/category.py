from django.views.generic import ListView, DetailView

from fints_downloader.models import Category


class CategoryList(ListView):
    template_name = 'categories.html'
    model = Category
    context_object_name = 'categories'
    # paginate_by = 10

    # def get_queryset(self):
    #     return super().get_queryset().exclude(type=AccountTypes.FOREIGN)


class CategoryDetail(DetailView):
    template_name = 'category.html'
    model = Category
