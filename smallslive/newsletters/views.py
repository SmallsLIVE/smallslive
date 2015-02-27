from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView
from .models import Newsletter


class NewsletterListView(ListView):
    model = Newsletter
    context_object_name = 'newsletters'
    template_name = 'newsletters/newsletter_list.html'

newsletter_list = NewsletterListView.as_view()
