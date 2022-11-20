from django.shortcuts import render
# Create your views here.
from django.template import loader
from .models import Profile, Post
from .forms import UserCreationForm
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth import login
from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView

class Index_view(TemplateView):
    template_name = "catalog/index.html"

class Feed_view(TemplateView):
    template_name = "catalog/feed.html"

class Home_view(LoginView):
    template_name = "catalog/home.html"
    next_page = reverse("catalog:feed")
    redirect_authenticated_user = True

class SignUp_view(CreateView):
    template_name = "catalog/sign_up.html"
    form_class = UserCreationForm

    def form_valid(self, form):
        base_user = BaseUser.objects.create_user(
            username = form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data["email"],
        )
        Profile.objects.create(
            _base_user=base_user,
            name=form.cleaned_data['name'],
        )
        login(self.request, base_user)

        return redirect('catalog:profile')

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form)
        )

class Profile_view(TemplateView):
    login_url = "/home/"
    template_name = "catalog/profile.html" 



class Profile1_view(TemplateView):
    template_name = "catalog/profile1.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_in_html"] = Profile.objects.get(user__username='dave')
        context["post"] = Post.objects.get()
        return context

class Profile2_view(TemplateView):
    template_name = "catalog/profile2.html"
