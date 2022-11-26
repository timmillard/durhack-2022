"""
    Views in pulsifi application.
"""

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView

from .forms import UserCreationForm
from .models import Profile


class Home_View(LoginView):
    template_name = "pulsifi/home.html"
    next_page = "pulsifi:feed"
    redirect_authenticated_user = True


class Feed_View(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("pulsifi:home")
    template_name = "pulsifi/feed.html"


class Self_Profile_View(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("pulsifi:home")
    template_name = "pulsifi/profile.html"


class ID_Profile_View(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy("pulsifi:home")

class Create_Post_View(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy("pulsifi:home")


class Signup_View(CreateView):
    template_name = "pulsifi/signup.html"
    form_class = UserCreationForm

    def form_valid(self, form):
        base_user = BaseUser.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            email=form.cleaned_data["email"],
        )
        Profile.objects.create(
            _base_user=base_user,
            name=form.cleaned_data["name"],
        )
        login(self.request, base_user)

        return redirect("pulsifi:profile")

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form)
        )