from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from fints_downloader.models.category import Category


class CategoryList(LoginRequiredMixin, ListView):
    template_name = "categories.html"
    model = Category
    context_object_name = "categories"
    # paginate_by = 10

    # def get_queryset(self):
    #     return super().get_queryset().exclude(type=AccountTypes.FOREIGN)


class CategoryDetail(LoginRequiredMixin, DetailView):
    template_name = "category.html"
    model = Category
