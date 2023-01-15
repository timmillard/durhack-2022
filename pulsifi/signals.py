from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Model
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import User, _User_Generated_Content_Model


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
@receiver(post_save, sender=get_user_model())
def super_user_added_to_admins_group_or_moderator_made_staff(sender, instance: User, **kwargs):
    if instance.is_superuser:
        admin_group_QS = Group.objects.filter(name="Admins")

        if admin_group_QS.exists():
            admin_group = admin_group_QS.get()
            if admin_group not in instance.groups.all():
                instance.groups.add(admin_group)  # FIXME: group not being added to user

    if not instance.is_staff and set(Group.objects.filter(name="Moderators").values_list('id', flat=True)).issubset(set(instance.groups.all().values_list('id', flat=True))):
        instance.update(is_staff=True)
