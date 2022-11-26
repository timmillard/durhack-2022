"""
    Views in pulsifi application.
"""

from django.contrib.auth import login
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView

from .forms import UserCreationForm
from .models import Profile


class Index_view(TemplateView):
    template_name = "pulsifi/index.html"


class Feed_view(TemplateView):
    template_name = "pulsifi/feed.html"


class Home_view(LoginView):
    template_name = "pulsifi/home.html"
    next_page = "pulsifi:feed"
    redirect_authenticated_user = True


class Signup_view(CreateView):
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


class Profile_view(TemplateView):
    login_url = "/home/"
    template_name = "pulsifi/profile.html"


class Profile1_view(TemplateView):
    template_name = "pulsifi/profile1.html"


class Profile2_view(TemplateView):
    template_name = "pulsifi/profile2.html"