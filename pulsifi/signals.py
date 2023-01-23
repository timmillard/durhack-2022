import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Pulse, Reply, User, _User_Generated_Content_Model

logger = logging.getLogger(__name__)


def ready():
    pass


# noinspection PyUnusedLocal
@receiver(m2m_changed, sender=_User_Generated_Content_Model.liked_by.through)
@receiver(m2m_changed, sender=_User_Generated_Content_Model.disliked_by.through)
def user_in_liked_and_disliked_or_creator_in_liked_or_disliked(sender, instance: User | Pulse | Reply, action: str, reverse: bool, model, pk_set: set[int], **kwargs):
    if isinstance(instance, _User_Generated_Content_Model) and not reverse:
        for user in model.objects.filter(id__in=pk_set):
            if action == "pre_add":
                if sender == instance.liked_by.through and instance.disliked_by.filter(id=user.id).exists():
                    instance.disliked_by.remove(user)

                elif sender == instance.disliked_by.through and instance.liked_by.filter(id=user.id).exists():
                    instance.liked_by.remove(user)

            elif action == "post_add":
                if sender == instance.liked_by.through and user == instance.creator:
                    instance.liked_by.remove(user)

                if sender == instance.disliked_by.through and user == instance.creator:
                    instance.disliked_by.remove(user)

    elif isinstance(instance, get_user_model()) and reverse:
        for content in model.objects.filter(id__in=pk_set):
            if action == "pre_add":
                if sender == instance.liked_pulse_set.through and instance.disliked_pulse_set.filter(id=content.id).exists():
                    instance.disliked_pulse_set.remove(content)

                elif sender == instance.disliked_pulse_set.through and instance.liked_pulse_set.filter(id=content.id).exists():
                    instance.liked_pulse_set.remove(content)

                elif sender == instance.liked_reply_set.through and instance.disliked_reply_set.filter(id=content.id).exists():
                    instance.disliked_reply_set.remove(content)

                elif sender == instance.disliked_reply_set.through and instance.liked_reply_set.filter(id=content.id).exists():
                    instance.liked_reply_set.remove(content)

            elif action == "post_add":
                if sender == instance.liked_pulse_set.through and content.creator == instance:
                    instance.liked_pulse_set.remove(content)

                if sender == instance.disliked_pulse_set.through and content.creator == instance:
                    instance.disliked_pulse_set.remove(content)

                if sender == instance.liked_reply_set.through and content.creator == instance:
                    instance.liked_reply_set.remove(content)

                if sender == instance.disliked_reply_set.through and content.creator == instance:
                    instance.disliked_reply_set.remove(content)


# noinspection PyUnusedLocal
@receiver(m2m_changed, sender=get_user_model().groups.through)
def user_in_moderator_group_made_staff(sender, instance: User | Group, action: str, reverse: bool, model, pk_set: set[int], **kwargs):
    if action == "post_add":
        if isinstance(instance, get_user_model()) and not reverse:
            instance.ensure_user_in_moderator_or_admin_group_is_staff()

        elif isinstance(instance, Group) and reverse:
            existing_groups = []
            staff_group_name: str
            for staff_group_name in get_user_model().STAFF_GROUP_NAMES:
                group_QS = Group.objects.filter(name=staff_group_name)
                if group_QS.exists():
                    existing_groups.append(group_QS.get())

            if instance in existing_groups:
                user: User
                for user in model.objects.filter(id__in=pk_set):
                    user.ensure_user_in_moderator_or_admin_group_is_staff()

    if action == "post_remove" or action == "post_clear":
        if isinstance(instance, get_user_model()) and not reverse:
            instance.ensure_superuser_in_admin_group()

        elif isinstance(instance, Group) and reverse:
            admin_group_QS = Group.objects.filter(name="Admins")
            if admin_group_QS.exists():
                admin_group = admin_group_QS.get()
                if instance == admin_group:
                    if pk_set:
                        check_admin_users = model.objects.filter(id__in=pk_set, is_superuser=True)
                    else:
                        check_admin_users = model.objects.filter(is_superuser=True)

                    user: User
                    for user in check_admin_users:
                        user.ensure_superuser_in_admin_group()


# noinspection PyUnusedLocal
@receiver(m2m_changed, sender=get_user_model().following.through)
def prevent_follow_self(sender, instance: User, action: str, reverse: bool, model, pk_set: set[int], **kwargs):
    if action == "pre_add":
        if instance.id in pk_set:
            pk_set.remove(instance.id)
