"""
    Views in pulsifi application.
"""
from urllib.parse import unquote as urllib_unquote

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from .forms import ReplyForm, UserCreationForm
from .models import BaseUser, Profile, Pulse, Reply


class EditPulseOrReplyMixin(TemplateResponseMixin, ContextMixin):
    request: WSGIRequest

    def check_like_or_dislike_in_post_request(self):
        if "action" in self.request.POST:
            action: str = self.request.POST["action"]
            if action == "like" and "likeable_object" in self.request.POST:
                actionable_object = self.request.POST["likeable_object"]
                actionable_object.like()
            elif action == "dislike" and "dislikeable_object" in self.request.POST:
                actionable_object = self.request.POST["dislikeable_object"]
                actionable_object.dislike()
            else:
                return False
            return action, actionable_object
        else:
            return False

    def check_reply_in_post_request(self):
        if "action" in self.request.POST:
            action: str = self.request.POST["action"]
            if action == "reply":
                form = ReplyForm(self.request.POST)
                if form.is_valid():
                    reply: Reply = form.save()
                    return reply
                else:
                    return form
            else:
                return False
        else:
            return False

    def check_report_in_post_request(self):  # TODO: Create check_report_in_post_request functionality
        pass

    def check_edit_in_post_request(self):
        if self.check_like_or_dislike_in_post_request():
            return redirect(self.request.path_info)
        elif reply := self.check_reply_in_post_request():
            if isinstance(reply, Reply):
                return redirect(f"""{reverse("pulsifi:feed")}?highlight={reply.parent_object.id}""")
            elif isinstance(reply, ReplyForm):
                return self.render_to_response(self.get_context_data(form=reply))
        # TODO: what to do if a post is reported
        # elif self.check_report_in_post_request():
        #     if isinstance()
        else:
            return False


class Home_View(LoginView):  # TODO: toast for account deletion, show admin link for super-users, ask to login when redirecting here (show modal)
    template_name = "pulsifi/home.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "New user successfully created!",
            extra_tags="user_creation"
        )
        return response


class Feed_View(EditPulseOrReplyMixin, LoginRequiredMixin, ListView):  # TODO: lookup how constant scroll pulses, POST actions for pulses & replies, only show pulse if within time & not unlisted & visible & not in any reports, show replies, only show replies and pulses of active non-reported users, toast for successful redirect after login, highlight pulse/reply at top of page
    template_name = "pulsifi/feed.html"
    context_object_name = "pulse_list"
    model = Pulse

    def get_queryset(self):
        queryset = Pulse.objects.filter(
            creator__id__in=Profile.objects.get(
                _base_user__id=self.request.user.id
            ).following.exclude(
                _base_user__is_active=False
            ).values_list("id", flat=True)
        ).order_by("_date_time_created")

        print(queryset)
        if self.request.method == "GET" and "highlight" in self.request.GET:
            print(self.context_object_name)
            return queryset.exclude(id=int(self.request.GET["highlight"]))
        return queryset

    def post(self, request, *args, **kwargs):
        if response := self.check_edit_in_post_request():
            return response
        else:
            return HttpResponseBadRequest()


class Self_Profile_View(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return ID_Profile_View.as_view()(
            self.request,
            profile_id=Profile.objects.get(_base_user__id=self.request.user.id).id
        )

    def post(self, request, *args, **kwargs):
        return ID_Profile_View.as_view()(
            self.request,
            profile_id=Profile.objects.get(_base_user__id=self.request.user.id).id
        )


class ID_Profile_View(EditPulseOrReplyMixin, LoginRequiredMixin, DetailView):  # TODO: lookup how constant scroll pulses, POST actions for pulses & replies, only show pulse if within time, change profile parts (if self profile), delete pulse or account with modal (if self profile), show replies, toast for account creation, only show replies and pulses of active users
    model = Profile
    pk_url_kwarg = "profile_id"
    template_name = "pulsifi/profile.html"

    def check_delete_in_post_request(self):  # TODO: Create check_delete_in_post_request functionality
        pass

    def post(self, request, *args, **kwargs):
        if response := self.check_edit_in_post_request():
            return response
        # TODO: what to do if a post is deleted
        # elif self.check_delete_in_post_request():
        #     return redirect("pulsifi:feed")
        else:
            return HttpResponseBadRequest()


# TODO: profile search view, leaderboard view


class Create_Pulse_View(LoginRequiredMixin, CreateView):
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

        if "next" in self.request.POST:
            return redirect(urllib_unquote(self.request.POST["next"]))
        else:
            return redirect("pulsifi:self_profile")

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# TODO: logout view, password change view