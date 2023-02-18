from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Pulse, Reply, User, _User_Generated_Content_Model


def ready() -> None:
    """ Initialise this module when importing & starting signal listeners. """

    pass


# noinspection PyUnusedLocal
@receiver(m2m_changed, sender=_User_Generated_Content_Model.liked_by.through)
@receiver(m2m_changed, sender=_User_Generated_Content_Model.disliked_by.through)
def user_in_liked_and_disliked_or_creator_in_liked_or_disliked(sender, instance: User | Pulse | Reply, action: str, reverse: bool, model, pk_set: set[int], **kwargs) -> None:
    """
        Event handler for when a user is added to the like & dislike list of a
        User_Generated_Content or a user is added to the like or dislike list
        of a User_Generated_Content that they are the creator of.
    """

    if isinstance(instance, _User_Generated_Content_Model) and not reverse:
        user: User
        for user in model.objects.filter(id__in=pk_set):
            if action == "pre_add":
                if sender == instance.liked_by.through and instance.disliked_by.filter(id=user.id).exists():  # NOTE: Remove the user from the disliked_by list if they were just added to the liked_by list
                    instance.disliked_by.remove(user)

                elif sender == instance.disliked_by.through and instance.liked_by.filter(id=user.id).exists():  # NOTE: Remove the user from the liked_by list if they were just added to the disliked_by list
                    instance.liked_by.remove(user)

            elif action == "post_add":
                if sender == instance.liked_by.through and user == instance.creator:  # NOTE: Remove the user from the liked_by list if they are the User_Generated_Content creator
                    instance.liked_by.remove(user)

                if sender == instance.disliked_by.through and user == instance.creator:  # NOTE: Remove the user from the disliked_by list if they are the User_Generated_Content creator
                    instance.disliked_by.remove(user)

    elif isinstance(instance, get_user_model()) and reverse:
        content: Pulse | Reply
        for content in model.objects.filter(id__in=pk_set):
            if action == "pre_add":
                if sender == instance.liked_pulse_set.through and instance.disliked_pulse_set.filter(id=content.id).exists():  # NOTE: Remove the pulse from the user's from the disliked_pulse_set if they just added that pulse to their liked_pulse_set
                    instance.disliked_pulse_set.remove(content)

                elif sender == instance.disliked_pulse_set.through and instance.liked_pulse_set.filter(id=content.id).exists():  # NOTE: Remove the pulse from the user's from the liked_pulse_set if they just added that pulse to their disliked_pulse_set
                    instance.liked_pulse_set.remove(content)

                elif sender == instance.liked_reply_set.through and instance.disliked_reply_set.filter(id=content.id).exists():  # NOTE: Remove the reply from the user's from the disliked_reply_set if they just added that reply to their liked_reply_set
                    instance.disliked_reply_set.remove(content)

                elif sender == instance.disliked_reply_set.through and instance.liked_reply_set.filter(id=content.id).exists():  # NOTE: Remove the reply from the user's from the liked_reply_set if they just added that reply to their disliked_reply_set
                    instance.liked_reply_set.remove(content)

            elif action == "post_add":
                if sender == instance.liked_pulse_set.through and content.creator == instance:  # NOTE: Remove the pulse from the user's from the liked_pulse_set if they are the pulse's creator
                    instance.liked_pulse_set.remove(content)

                if sender == instance.disliked_pulse_set.through and content.creator == instance:  # NOTE: Remove the pulse from the user's from the disliked_pulse_set if they are the pulse's creator
                    instance.disliked_pulse_set.remove(content)

                if sender == instance.liked_reply_set.through and content.creator == instance:  # NOTE: Remove the reply from the user's from the liked_reply_set if they are the reply's creator
                    instance.liked_reply_set.remove(content)

                if sender == instance.disliked_reply_set.through and content.creator == instance:  # NOTE: Remove the reply from the user's from the disliked_reply_set if they are the reply's creator
                    instance.disliked_reply_set.remove(content)


# noinspection PyUnusedLocal
@receiver(m2m_changed, sender=get_user_model().groups.through)
def user_in_moderator_group_made_staff_and_superuser_in_admin_group(sender, instance: User | Group, action: str, reverse: bool, model, pk_set: set[int], **kwargs) -> None:
    """
        Event handler for when a user is added to the Moderators/Admins group.
        All moderators should have the is_staff member set to True. All
        superusers should be part of the Admins group.
    """

    if action == "post_add":
        if isinstance(instance, get_user_model()) and not reverse:  # NOTE: Ensure a user added to the Moderators group is a staff member
            instance.ensure_user_in_any_staff_group_is_staff()

        elif isinstance(instance, Group) and reverse:  # NOTE: Ensure when a user has a group added to their groups_set, if it is the Moderators group they should have is_staff set to True
            if instance in Group.objects.filter(name__in=get_user_model().STAFF_GROUP_NAMES):
                user: User
                for user in model.objects.filter(id__in=pk_set):
                    user.ensure_user_in_any_staff_group_is_staff()

    if action == "post_remove" or action == "post_clear":
        if isinstance(instance, get_user_model()) and not reverse:  # NOTE: Ensure a superuser is still in the admins group after their group_set has been changed
            instance.ensure_superuser_in_admin_group()

        elif isinstance(instance, Group) and reverse:  # NOTE: Ensure all superusers in the changed admin group's user_set are still in the admin group's user set
            try:
                admin_group = Group.objects.get(name="Admins")
            except Group.DoesNotExist:
                pass
            else:
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
def prevent_follow_self(sender, instance: User, action: str, reverse: bool, model, pk_set: set[int], **kwargs) -> None:
    """ Event handler for when a user is added to their own following list. """

    if action == "pre_add" and instance.id in pk_set:
        pk_set.remove(instance.id)
