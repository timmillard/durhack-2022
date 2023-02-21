"""
    Views in pulsifi app.
"""
from typing import Type

from allauth.account.views import LoginView as Base_LoginView, SignupView as Base_SignupView
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import RedirectURLMixin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.urls import reverse
from django.views.generic import CreateView, RedirectView
from django.views.generic.base import ContextMixin, TemplateResponseMixin, TemplateView
from el_pagination.views import AjaxListView

from .exceptions import GetParameterError, RedirectionLoopError, UserAlreadyInSetError, UserAlreadyNotInSetError
from .forms import Login_Form, Reply_Form, Signup_Form
from .models import Pulse, Reply, User


class FollowUserMixin(TemplateResponseMixin, ContextMixin):
    request: WSGIRequest

    def check_follow_or_unfollow_in_post_request(self) -> bool | HttpResponse:
        try:
            action: str = self.request.POST["action"].lower()
        except KeyError:
            return False
        else:
            if action == "follow":
                try:
                    follow_user: User = get_user_model().objects.get(id=self.request.POST["follow_user_id"])
                except KeyError or get_user_model().DoesNotExist:
                    return False
                else:
                    if self.request.user not in follow_user.followers.all():
                        follow_user.followers.add(self.request.user)
                        return self.render_to_response(self.get_context_data())
                    else:
                        raise UserAlreadyInSetError(user=self.request.user, user_set=follow_user.followers.all())
            elif action == "unfollow":
                try:
                    unfollow_user: User = get_user_model().objects.get(id=self.request.POST["unfollow_user_id"])
                except KeyError or get_user_model().DoesNotExist:
                    return False
                else:
                    if self.request.user in unfollow_user.followers.all():
                        unfollow_user.followers.remove(self.request.user)
                        return self.render_to_response(self.get_context_data())
                    else:
                        raise UserAlreadyNotInSetError(user=self.request.user, user_set=unfollow_user.followers.all())
            else:
                return False


class EditPulseOrReplyMixin(TemplateResponseMixin, ContextMixin):
    request: WSGIRequest

    def check_like_or_dislike_in_post_request(self) -> bool | tuple[str, Pulse | Reply]:
        try:
            action: str = self.request.POST["action"]
        except KeyError:
            return False
        else:
            try:
                model: Type[Pulse | Reply] = apps.get_model(app_label="pulsifi", model_name=self.request.POST["actionable_model_name"])
            except KeyError:
                return False
            else:
                if action == "like":
                    try:
                        actionable_object: Pulse | Reply = model.objects.get(id=self.request.POST["likeable_object_id"])
                    except KeyError or model.DoesNotExist:
                        return False
                    else:
                        actionable_object.liked_by.add(self.request.user)
                        return action, actionable_object
                elif action == "dislike":
                    try:
                        actionable_object: Pulse | Reply = model.objects.get(id=self.request.POST["dislikeable_object_id"])
                    except KeyError or model.DoesNotExist:
                        return False
                    else:
                        actionable_object.disliked_by.add(self.request.user)
                        return action, actionable_object
                else:
                    return False

    def check_reply_in_post_request(self) -> bool | Reply | Reply_Form:
        try:
            action: str = self.request.POST["action"]
        except KeyError:
            return False
        else:
            if action == "reply":
                form = Reply_Form(self.request.POST)
                if form.is_valid():
                    reply: Reply = form.save()
                    return reply
                else:
                    return form
            else:
                return False

    def check_report_in_post_request(self):  # TODO: Create check_report_in_post_request functionality
        pass

    def check_action_in_post_request(self) -> bool | HttpResponse:
        if self.check_like_or_dislike_in_post_request():
            return self.render_to_response(self.get_context_data())
        elif reply := self.check_reply_in_post_request():
            if isinstance(reply, Reply):
                return redirect(reply)
            elif isinstance(reply, Reply_Form):
                return self.render_to_response(self.get_context_data(form=reply))
        # TODO: what to do if a post is reported
        # elif self.check_report_in_post_request():
        #     if isinstance()
        else:
            return False


class Home_View(RedirectURLMixin, TemplateView):  # TODO: toast for account deletion, show admin link for super-users, ask to log in when redirecting here (show modal), prevent users with >3 in progress reports or >0 completed reports from logging in (with reason page)
    template_name = "pulsifi/home.html"
    http_method_names = ["get"]

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.get_success_url()

            if redirect_to == self.request.path:
                raise RedirectionLoopError(redirect_to, "Redirection loop for authenticated user detected. Check that your LOGIN_REDIRECT_URL doesn't point to a login page.")

            return HttpResponseRedirect(redirect_to)

        return super().dispatch(request, *args, **kwargs)

    def get_default_redirect_url(self):
        return resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "login_form" not in kwargs and "login_form" not in self.request.session:
            context["login_form"] = Login_Form(prefix="login")

        elif "login_form" in kwargs:
            context["login_form"] = kwargs["login_form"]

        elif "login_form" in self.request.session:
            login_form = Login_Form(
                data=self.request.session["login_form"]["data"],
                request=self.request,
                prefix="login"
            )
            login_form.is_valid()

            context["login_form"] = login_form

            del self.request.session["login_form"]

        if "signup_form" not in kwargs and "signup_form" not in self.request.session:
            context["signup_form"] = Signup_Form(prefix="signup")

        elif "signup_form" in kwargs:
            context["signup_form"] = kwargs["signup_form"]

        elif "signup_form" in self.request.session:
            signup_form = Signup_Form(
                data=self.request.session["signup_form"]["data"],
                prefix="signup"
            )
            signup_form.is_valid()

            context["signup_form"] = signup_form

            del self.request.session["signup_form"]

        if self.request.method == "GET" and "action" in self.request.GET:
            if self.request.GET["action"] in ("login", "signup") and self.redirect_field_name in self.request.GET:
                context["redirect_field_value"] = self.request.GET[self.redirect_field_name]

        context["redirect_field_name"] = self.redirect_field_name

        return context


class Feed_View(EditPulseOrReplyMixin, LoginRequiredMixin, AjaxListView):  # TODO: lookup how constant scroll pulses, POST actions for pulses & replies, only show pulses/replies if within time & visible & creator is active+visible & not in any non-rejected reports, show replies, toast for successful redirect after login, highlight pulse/reply (from get parameters) at top of page or message if not visible
    template_name = "pulsifi/feed.html"
    object_list: QuerySet[Pulse]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object_list = self.get_queryset()

        context.update(
            {
                "pulse_list": self.object_list,
                "pagination_snippet": "pulsifi/feed_pagination_snippet.html"
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        try:
            return self.render_to_response(self.get_context_data())
        except GetParameterError:
            return HttpResponseBadRequest()

    def get_queryset(self):
        user: User = self.request.user
        queryset: QuerySet[Pulse] = user.get_feed_pulses()

        if self.request.method == "GET" and "highlight" in self.request.GET:
            highlight: str = self.request.GET["highlight"]

            try:
                return queryset.exclude(id=int(highlight))
            except ValueError as e:
                raise GetParameterError(get_parameters={"highlight": highlight}) from e

        return queryset

    def post(self, request, *args, **kwargs):
        if response := self.check_action_in_post_request():
            return response
        else:
            return HttpResponseBadRequest()


class Self_Account_View(LoginRequiredMixin, RedirectView):  # TODO: Show toast for users that have just signed up to edit their bio/avatar
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "pulsifi:specific_account",
            kwargs={"username": self.request.user.username}
        )


class Specific_Account_View(EditPulseOrReplyMixin, FollowUserMixin, LoginRequiredMixin, AjaxListView):  # TODO: lookup how constant scroll pulses, POST actions for pulses & replies, only show pulses/replies if within time & visible & creator is active+visible & not in any non-rejected reports, change profile parts (if self profile), delete account with modal or view all finished pulses (if self profile), show replies, toast for account creation, prevent create new pulses/replies if >3 in progress or >1 completed reports on user or pulse/reply of user
    template_name = "pulsifi/account.html"
    object_list = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "specific_account": get_object_or_404(
                    get_user_model(),
                    is_active=True,
                    username=self.kwargs.get("username")
                ),
                "pulse_list": self.get_queryset(),
                "pagination_snippet": "pulsifi/feed_pagination_snippet.html"
            }
        )

        return context

    def get_queryset(self):
        return get_object_or_404(
            get_user_model(),
            is_active=True,
            username=self.kwargs.get("username")
        ).created_pulse_set.all()

    def post(self, request, *args, **kwargs):  # TODO: only allow profile change actions (pic, bio, username(not already in use & using a form)) if view is for logged-in user
        if response := self.check_action_in_post_request():
            return response
        elif response := self.check_follow_or_unfollow_in_post_request():
            return response
        # TODO: what to do if a post is deleted
        # elif self.check_delete_in_post_request():
        #     return redirect("pulsifi:feed")
        else:
            return HttpResponseBadRequest()


# TODO: profile search view, leaderboard view, report views & moderator views


class Create_Pulse_View(LoginRequiredMixin, CreateView):
    pass


class Signup_POST_View(Base_SignupView):
    http_method_names = ["post"]
    redirect_authenticated_user = True
    prefix = "signup"

    def form_invalid(self, form):
        if "signup_form" in self.request.session:
            del self.request.session["signup_form"]

        self.request.session["signup_form"] = {
            "data": form.data,
            "errors": form.errors
        }

        return redirect(settings.SIGNUP_URL)


class Login_POST_View(Base_LoginView):
    http_method_names = ["post"]
    redirect_authenticated_user = True
    prefix = "login"

    def form_invalid(self, form):
        if "login_form" in self.request.session:
            del self.request.session["login_form"]

        self.request.session["login_form"] = {
            "data": form.data,
            "errors": form.errors
        }

        return redirect(settings.LOGIN_URL)

# TODO: password change view, confirm email view, manage emails view, password set after not having one because of social login view, forgotten password reset view, forgotten password reset success view, logout confirmation popup (toast)

# TODO: 2fa stuff!

# TODO: 404 error page, 403 forbidden page when reports cannot be created, other nicer error pages (look up all possible http errors)
