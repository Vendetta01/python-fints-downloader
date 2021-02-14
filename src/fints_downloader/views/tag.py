from django.views.generic import ListView, DetailView

from fints_downloader.models.tag import Tag


class TagListView(ListView):
    template_name = "tags.html"
    model = Tag
    context_object_name = "tags"
    # paginate_by = 10

    # def get_queryset(self):
    #    return super().get_queryset().exclude(type=AccountTypes.FOREIGN)


class TagView(DetailView):
    template_name = "tag.html"
    model = Tag

    # def get_context_data(self, *args, **kwargs):
    #    context = super(AccountView, self).get_context_data(*args, **kwargs)

    #    # context['num_banks'] = Bank.objects.count()

    #    return context
