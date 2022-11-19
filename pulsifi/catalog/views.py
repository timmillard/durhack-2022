from django.shortcuts import render
# Create your views here.

from django.http import HttpResponse

from django.template import loader

from django.views.generic import TemplateView

class Index(TemplateView):
    template_name = "catalog/index.html"

class Feed(TemplateView):
    template_name = "catalog/feed.html"

class Home(TemplateView):
    template_name = "catalog/home.html"

class Profile(TemplateView):
    template_name = "catalog/profile.html"