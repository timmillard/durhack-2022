from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Model
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import _User_Generated_Content_Model


def ready():
    pass


# noinspection PyUnusedLocal
@receiver(m2m_changed, sender=_User_Generated_Content_Model.liked_by.through)
@receiver(m2m_changed, sender=_User_Generated_Content_Model.disliked_by.through)
def user_in_liked_and_disliked_or_creator_in_liked_or_disliked(sender, instance, action: str, reverse: bool, model: type(Model), pk_set: list[int], **kwargs):
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
def user_in_moderators_group_made_staff(sender, instance, action: str, reverse: bool, model: type(Model), pk_set: list[int], **kwargs):
    if action == "post_add":
        if isinstance(instance, get_user_model()) and not reverse:
            moderator_group = Group.objects.filter(name="Moderators").first()
            if moderator_group and moderator_group in instance.groups.all():
                instance.update(is_staff=True)

        elif isinstance(instance, Group) and reverse:
            moderator_group = Group.objects.filter(name="Moderators").first()
            if moderator_group and instance == moderator_group:
                for user in get_user_model().objects.filter(id__in=pk_set):
                    user.update(is_staff=True)
