"""
    Views in pulsifi app.
"""

from allauth.account.views import SignupView as Base_SignupView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as Base_LoginView, RedirectURLMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, RedirectView
from django.views.generic.base import ContextMixin, TemplateResponseMixin, TemplateView

from .exceptions import RedirectionLoopError
from .forms import Login_Form, Reply_Form, Signup_Form
from .models import Pulse, Reply, User


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
                form = Reply_Form(self.request.POST)
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

    def check_action_in_post_request(self):
        if self.check_like_or_dislike_in_post_request():
            return redirect(self.request.path_info)
        elif reply := self.check_reply_in_post_request():
            if isinstance(reply, Reply):
                return redirect(f"""{reverse("pulsifi:feed")}?highlight={reply.replied_content.id}""")
            elif isinstance(reply, Reply_Form):
                return self.render_to_response(self.get_context_data(form=reply))
        # TODO: what to do if a post is reported
        # elif self.check_report_in_post_request():
        #     if isinstance()
        else:
            return False


class Home_View(RedirectURLMixin, TemplateView):  # TODO: toast for account deletion, show admin link for super-users, ask to log in when redirecting here (show modal), prevent users with >3 in progress reports or >0 completed reports from logging in (with reason page)
    template_name = "pulsifi/home.html"  # BUG: errors raised by the model's clean() method are not caught and turned to formatted error messages (they propagate up and cause a server error 500

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

        if "login_form" not in kwargs:
            context["login_form"] = Login_Form(
                self.request, prefix="login"
            )

        if "signup_form" not in kwargs:
            context["signup_form"] = Signup_Form(prefix="signup")

        if self.request.method == "GET" and "action" in self.request.GET:
            if self.request.GET["action"] in ("login", "signup") and self.redirect_field_name in self.request.GET:
                context["redirect_field_value"] = self.request.GET[self.redirect_field_name]

        current_site = get_current_site(self.request)
        context.update(
            {
                "redirect_field_name": self.redirect_field_name,
                "site": current_site,
                "site_name": current_site.name
            }
        )  # TODO: check whether these values are needed in template rendering & remove them if unnecessary
        print(f"redirect_field_value {context}")
        return context


class Feed_View(EditPulseOrReplyMixin, LoginRequiredMixin, ListView):  # TODO: lookup how constant scroll pulses, POST actions for pulses & replies, only show pulses/replies if within time & visible & creator is active+visible & not in any non-rejected reports, show replies, toast for successful redirect after login, highlight pulse/reply (from get parameters) at top of page or message if not visible
    template_name = "pulsifi/feed.html"
    context_object_name = "pulse_list"
    model = Pulse

    def get_queryset(self):  # TODO: get queryset from models.py not views.py
        # noinspection PyUnresolvedReferences
        queryset = Pulse.objects.filter(
            creator__id__in=self.request.user.following.exclude(
                is_active=False
            ).values_list("id", flat=True)
        ).order_by("_date_time_created")

        if self.request.method == "GET" and "highlight" in self.request.GET:
            return queryset.exclude(id=int(self.request.GET["highlight"]))
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


class Specific_Account_View(EditPulseOrReplyMixin, LoginRequiredMixin, DetailView):  # TODO: lookup how constant scroll pulses, POST actions for pulses & replies, only show pulses/replies if within time & visible & creator is active+visible & not in any non-rejected reports, change profile parts (if self profile), delete account with modal or view all finished pulses (if self profile), show replies, toast for account creation, prevent create new pulses/replies if >3 in progress or >1 completed reports on user or pulse/reply of user
    template_name = "pulsifi/account.html"

    def get_object(self, queryset: QuerySet[User] = None):
        if queryset is None:
            queryset = get_user_model().objects.all()
        try:  # TODO: Replace with get object or 404
            obj: User = queryset.filter(is_active=True).get(username=self.kwargs.get("username"))
        except queryset.model.DoesNotExist:
            # noinspection PyProtectedMember
            raise Http404(f"That {queryset.model._meta.verbose_name} does not exist.")
        return obj

    def post(self, request, *args, **kwargs):  # TODO: only allow profile change actions (pic, bio, username(not already in use & using a form)) if view is for logged-in user
        if response := self.check_action_in_post_request():
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

    def form_invalid(self, form):
        # TODO: send errors as messages
        return redirect(settings.SIGNUP_URL)  # BUG: form looses filled in values because redirected to signup URL


class Login_POST_View(Base_LoginView):  # TODO: change to allauth login
    template_name = None
    form_class = Login_Form  # TODO: move to base_settings.py when using allauth login
    http_method_names = ["post"]
    redirect_authenticated_user = True

    def form_invalid(self, form):
        # TODO: send errors as messages
        return redirect(settings.LOGIN_URL)  # BUG: form looses filled in values because redirected to login URL

    # TODO: logout view, password change view, confirm email view, manage emails view, password set after not having one because of social login view, forgotten password reset view, forgotten password reset success view

# TODO: 2fa stuff!

# TODO: 404 error page, 403 forbidden page when reports cannot be created, other nicer error pages (look up all possible http errors)
