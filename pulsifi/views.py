"""
    Views in pulsifi application.
"""

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.views import LoginView
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import ReplyForm, UserCreationForm
from .models import Post, Profile


class LikeAndDislikeMixin:
    @staticmethod
    def check_like_or_dislike_in_post_request(request):
        try:
            if request.POST["action"] == "like":
                request.POST["likeable_object"].like()
                return f"{request.POST['likeable_object'].__class__.__name__} was liked"
            elif request.POST["action"] == "dislike":
                request.POST["dislikeable_object"].dislike()
                return f"{request.POST['likeable_object'].__class__.__name__} was disliked"
        except KeyError:
            return False


class ReplyMixin:
    def check_reply_in_post_request(self, request):
        try:
            if request.POST["action"] == "reply":
                form = ReplyForm(request.POST)
                if form.is_valid():
                    reply = form.save()
                    return redirect("catalog:display_post", post_id=reply.parent_object.id)
                else:
                    return self.render_to_response(self.get_context_data(form=form))

        except KeyError:
            return False

class Home_View(LoginView):
    template_name = "pulsifi/home.html"
    next_page = "pulsifi:feed"
    redirect_authenticated_user = True


class Feed_View(LikeAndDislikeMixin, ReplyMixin, LoginRequiredMixin, ListView):
    template_name = "pulsifi/feed.html"

    def get_queryset(self):
        return Post.objects.filter(
            creator__id__in=Profile.objects.get(
                _base_user__id=self.request.user.id
            ).following.all().values_list("id", flat=True)
        ).order_by("_date_time_created")

    def post(self, request, *args, **kwargs):
        if self.check_like_or_dislike_in_post_request(request) is False or self.check_reply_in_post_request(request) is False:
            return HttpResponseBadRequest()
        else:
            return redirect(self.request.path_info)


class Self_Profile_View(LoginRequiredMixin, TemplateView):
    template_name = "pulsifi/profile.html"


class ID_Profile_View(LoginRequiredMixin, DetailView):
    pass


class Create_Post_View(LoginRequiredMixin, CreateView):
    pass


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

        return redirect("pulsifi:self_profile")

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))