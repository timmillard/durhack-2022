from django.shortcuts import render
# Create your views here.
from django.template import loader
from django.views.generic import TemplateView
from .models import Profile

class Index(TemplateView):
    template_name = "catalog/index.html"

class Feed(TemplateView):
    template_name = "catalog/feed.html"

class Home(TemplateView):
    template_name = "catalog/home.html"

class Profile(TemplateView):
    template_name = "catalog/profile.html"


class Profile1(TemplateView):
    template_name = "catalog/profile1.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_in_html"] = Profile.objects.get(user__username='dave')
        return context