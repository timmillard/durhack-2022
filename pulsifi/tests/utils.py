"""
    Utility classes for pulsifi app test suite.
"""
from typing import Iterable

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import ManyToManyField, Model
from django.test import TestCase

from pulsifi.models import Pulse, Reply, User


class Base_TestCase(TestCase):
    def setUp(self):
        Group.objects.create(name="Admins")
        Group.objects.create(name="Moderators")


class CreateTestUserHelper:
    GENERATABLE_OBJECTS = ["user"]
    # noinspection SpellCheckingInspection
    TEST_USERS = [
        {"username": "padgriffin", "password": "#2@cqt", "email": "padgriffin@gmail.com", "bio": "TV maven. Evil thinker. Infuriatingly humble gamer. Communicator. Pop culture advocate."},
        {"username": "Extralas55", "password": "321321", "email": "green.anna@hotmail.co.uk", "bio": "The superhero movie was good but they didn't cover the part in his life where he co-founded a pizza restaurant... I assume that will be in the sequel..."},
        {"username": "Rines1970", "password": "chicken1", "email": "robyn1973@yahoo.com", "bio": "Just explained drain cleaning to my friend. I don't think I did it right, as she's excited to get started."},
        {"username": "Requit", "password": "pa55word", "email": "alexander.griffiths@shaw.com", "bio": "Our parents blame it on the generation but do they think about who raised us."},
        {"username": "Nionothe", "password": "turnedrealizeroyal", "email": "pjackpppson@stewart.com", "bio": "Amateurs build planes, professionals built the titanic, how do you feel now?"},
        {"username": "neha_schumm", "password": "1q2w3e4r", "email": "iyoung@gmail.com", "bio": "When life gives you lemons, throw them back"},
        {"username": "Myseat59", "password": "password", "email": "viva_konopels@hotmail.com", "bio": "I saw some girl texting and driving the other day and it made me really angry. So I rolled my window down and threw my coffee at her."},
        {"username": "Tunt1978", "password": "OoYoa9ahf", "email": "rachael2001@gmail.com", "bio": "Liberalism is trust of the people tempered by prudence. Conservatism is distrust of the people tempered by fear."},
        {"username": "eesait4Oo", "password": "323232", "email": "julia_scott99@reynolds.com", "bio": "As I said before, I never repeat myself."},
        {"username": "Therhatim", "password": "JORDAN", "email": "ken80@jones.net", "bio": "That awkward moment when you are at a funeral and your phone rings.. your ring tone is 'I Will Survive'."},
        {"username": "Repostity", "password": "aequei3Eequ", "email": "simpson.mark@clark.co.uk", "bio": "Just had a beer and a taco, and now bout to finish my laundry"},
        {"username": "Proodents445", "password": "teddybea", "email": "AlfieOsborne@dayrep.com", "bio": "'The best revenge is to live on and prove yourself' - Eddie Vedder"},
        {"username": "Hassaid", "password": "vh5150", "email": "holly65@gmail.com", "bio": "Zombie trailblazer & unapologetic troublemaker."},
        {"username": "alexzander", "password": "PulsifiPass123", "email": "khan.imogen@gmail.com", "bio": "Jury duty on Monday...That in itself is a joke"},
        {"username": "annalise", "password": "24101984", "email": "jessica.price@outlook.com", "bio": "Love is the ultimate theme"},
        {"username": "walter.her1992", "password": "18atcskd2w", "email": "christian40@bell.biz", "bio": "The relationship between the Prime Minister and the Head Of State"},
        {"username": "rodger.nader", "password": "letmein", "email": "norene.nikola@gmail.com", "bio": "Bacon fanatic"},
        {"username": "lorenz._fri1988", "password": "monkey", "email": "Exielenn@studentmail.net", "bio": "My personal style is best described as 'didn't expect to have to get out of the car'"},
        {"username": "grayson", "password": "Iloveyou", "email": "gus2017@hotmail.com", "bio": "Just taught my kids about taxes by eating 38% of their ice cream"},
        {"username": "Professor_T", "password": "lung-calf-trams", "email": "trofessor-t@trofessor-t.com", "bio": "Haven't gotten ONE response to my hospital job applications"}
    ]
    _test_users_index = -1

    @classmethod
    def create_test_user(cls, save=True, **kwargs) -> User:
        if kwargs:
            if "username" not in kwargs or "password" not in kwargs or "email" not in kwargs or "bio" not in kwargs:
                cls._test_users_index = (cls._test_users_index + 1) % len(cls.TEST_USERS)

            if "username" in kwargs:
                username = kwargs.pop("username")
            else:
                username = cls.TEST_USERS[cls._test_users_index]["username"]
            if "password" in kwargs:
                password = kwargs.pop("password")
            else:
                password = cls.TEST_USERS[cls._test_users_index]["password"]
            if "email" in kwargs:
                email = kwargs.pop("email")
            else:
                email = cls.TEST_USERS[cls._test_users_index]["email"]
            if "bio" in kwargs:
                bio = kwargs.pop("bio")
            else:
                bio = cls.TEST_USERS[cls._test_users_index]["bio"]

            if "visible" in kwargs or "verified" in kwargs or "is_superuser" in kwargs or "is_staff" in kwargs or "is_active" in kwargs:
                if "visible" in kwargs:
                    is_active = kwargs["visible"]
                    if "is_active" in kwargs:
                        if kwargs["is_active"] != is_active:
                            raise ValueError("User attribute <visible> cannot be set to a different value from the User attribute <is_active>.")

                    if save:
                        return get_user_model().objects.create_user(
                            username=username,
                            password=password,
                            email=email,
                            is_active=is_active,
                            bio=bio,
                            **kwargs
                        )

                    return get_user_model()(
                        username=username,
                        password=password,
                        email=email,
                        is_active=is_active,
                        bio=bio,
                        **kwargs
                    )

                if save:
                    return get_user_model().objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        bio=bio,
                        **kwargs
                    )

                return get_user_model()(
                    username=username,
                    password=password,
                    email=email,
                    bio=bio,
                    **kwargs
                )

            if save:
                return get_user_model().objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    bio=bio
                )

            return get_user_model()(
                username=username,
                password=password,
                email=email,
                bio=bio
            )

        else:
            cls._test_users_index = (cls._test_users_index + 1) % len(cls.TEST_USERS)

            if save:
                return get_user_model().objects.create_user(
                    username=cls.TEST_USERS[cls._test_users_index]["username"],
                    password=cls.TEST_USERS[cls._test_users_index]["password"],
                    email=cls.TEST_USERS[cls._test_users_index]["email"],
                    bio=cls.TEST_USERS[cls._test_users_index]["bio"]
                )
            return get_user_model()(
                username=cls.TEST_USERS[cls._test_users_index]["username"],
                password=cls.TEST_USERS[cls._test_users_index]["password"],
                email=cls.TEST_USERS[cls._test_users_index]["email"],
                bio=cls.TEST_USERS[cls._test_users_index]["bio"]
            )

    @classmethod
    def get_test_unknown_field(cls, field_name: str):
        if field_name == "bio":
            return cls.create_test_user(save=False).bio
        elif field_name == "username":
            return cls.create_test_user(save=False).username
        elif field_name == "password":
            return cls.create_test_user(save=False).password
        elif field_name == "email":
            return cls.create_test_user(save=False).email
        else:
            raise ValueError(f"Given field_name ({field_name}) is not one that can have test values created for it.")


class GetFieldsHelper:
    @staticmethod
    def get_non_relation_fields(model: Model, exclude: Iterable[str] = None):
        if exclude is None:
            exclude = []

        return [field for field in model._meta.get_fields() if field.name not in exclude and field.name != "+" and not field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, GenericRelation)]

    @staticmethod
    def get_single_relation_fields(model: Model, exclude: Iterable[str] = None):
        if exclude is None:
            exclude = []

        return [field for field in model._meta.get_fields() if field.name not in exclude and field.name != "+" and field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, GenericRelation)]

    @staticmethod
    def get_multi_relation_fields(model: Model, exclude: Iterable[str] = None):
        if exclude is None:
            exclude = []

        return [field for field in model._meta.get_fields() if field.name not in exclude and field.name != "+" and (isinstance(field, ManyToManyField) or isinstance(field, GenericRelation))]


class CreateTestUserGeneratedContentHelper:
    GENERATABLE_OBJECTS = ["pulse", "reply"]
    TEST_MESSAGES = [
        "This Vodka says, everything will be okay. At least for a few hours.",
        "Can anyone tell me the name of that romance movie? You know, the one where she plays the quirky girl who ultimately finds love in the end?",
        "Some people are so afraid do die that they never begin to live.",
        "There's a special place in he'll for autocorrect",
        "I do not think that marriage is one of my talents. I've been much happier unmarried than married.",
        "There comes a time when you just look at yourself in the mirror, and say \"this is as good as it's gonna get.\"",
        "I think I'll always be famous. I just hope I don't become infamous.",
        "The principle of art is to pause, not bypass.",
        "Being smart doesn't stop you from doing stupid things.",
        "I am writing a 360 page book...I'm making progress...I already have all the page numbers done",
        "I never saw any of my dad's stories. My mother said he had piles and piles of manuscripts.",
        "Wisdom finds its literary expression in wisdom literature.",
        "If you're not fully satisfied with your life, do something about it. Or complain about it on the internet. Whatever.",
        "I am a great believer in luck, and I find the harder I work the more I have of it.",
        "It's weird how many of my ancestors were sepia-toned.",
        "The best way to keep your kids out of hot water is to put some dishes in it.",
        "My beer never tells me it has a girlfriend.",
        "The truth is lived, not taught.",
        "My grandfather was a lawyer",
        "I work with really cool people"
    ]
    _test_message_index = -1

    @classmethod
    def create_test_user_generated_content(cls, model: str, save=True, **kwargs):
        if model not in ("pulse", "reply"):
            raise ValueError(f"""{model} is not a valid choice for parameter "model", choose one of: "pulse", "reply".""")

        if model == "pulse":
            return cls._create_test_pulse(save, **kwargs)
        elif model == "reply":
            return cls._create_test_reply(save, **kwargs)

    @classmethod
    def _create_test_pulse(cls, save=True, **kwargs):
        if kwargs:
            if "message" not in kwargs:
                cls._test_message_index = (cls._test_message_index + 1) % len(cls.TEST_MESSAGES)
                message = cls.TEST_MESSAGES[cls._test_message_index]
            else:
                message = kwargs.pop("message")

            if "visible" in kwargs:
                visible = kwargs.pop("visible")

                if "creator" in kwargs:
                    if save:
                        return Pulse.objects.create(
                            message=message,
                            creator=kwargs.pop("creator"),
                            visible=visible
                        )

                    return Pulse(
                        message=message,
                        creator=kwargs.pop("creator"),
                        visible=visible
                    )
                if save:
                    return get_user_model().objects.create(
                        message=message,
                        creator=CreateTestUserHelper.create_test_user(**kwargs),
                        visible=visible
                    )

                return Pulse(
                    message=message,
                    creator=CreateTestUserHelper.create_test_user(**kwargs),
                    visible=visible
                )

            if "creator" in kwargs:
                if save:
                    return Pulse.objects.create(
                        message=message,
                        creator=kwargs.pop("creator")
                    )

                return Pulse(
                    message=message,
                    creator=kwargs.pop("creator")
                )
            if save:
                return Pulse.objects.create(
                    message=message,
                    creator=CreateTestUserHelper.create_test_user(**kwargs)
                )

            return Pulse(
                message=message,
                creator=CreateTestUserHelper.create_test_user(**kwargs)
            )

        else:
            cls._test_message_index = (cls._test_message_index + 1) % len(cls.TEST_MESSAGES)

            if save:
                return Pulse.objects.create(
                    message=cls.TEST_MESSAGES[cls._test_message_index],
                    creator=CreateTestUserHelper.create_test_user()
                )

            return Pulse(
                message=cls.TEST_MESSAGES[cls._test_message_index],
                creator=CreateTestUserHelper.create_test_user()
            )

    @classmethod
    def _create_test_reply(cls, save=True, **kwargs):
        if kwargs:
            if "message" not in kwargs:
                cls._test_message_index = (cls._test_message_index + 1) % len(cls.TEST_MESSAGES)
                message = cls.TEST_MESSAGES[cls._test_message_index]
            else:
                message = kwargs.pop("message")

            if "replied_content" in kwargs:
                replied_content = kwargs.pop("replied_content")

                if "visible" in kwargs:
                    visible = kwargs.pop("visible")

                    if "creator" in kwargs:
                        if save:
                            return Reply.objects.create(
                                message=message,
                                creator=kwargs.pop("creator"),
                                visible=visible,
                                replied_content=replied_content
                            )

                        return Reply(
                            message=message,
                            creator=kwargs.pop("creator"),
                            visible=visible,
                            replied_content=replied_content
                        )
                    if save:
                        return Reply.objects.create(
                            message=message,
                            creator=CreateTestUserHelper.create_test_user(**kwargs),
                            visible=visible,
                            replied_content=replied_content
                        )

                    return Reply(
                        message=message,
                        creator=CreateTestUserHelper.create_test_user(**kwargs),
                        visible=visible,
                        replied_content=replied_content
                    )

                if "creator" in kwargs:
                    if save:
                        return Reply.objects.create(
                            message=message,
                            creator=kwargs.pop("creator"),
                            replied_content=replied_content
                        )

                    return Reply(
                        message=message,
                        creator=kwargs.pop("creator"),
                        replied_content=replied_content
                    )
                if save:
                    return Reply.objects.create(
                        message=message,
                        creator=CreateTestUserHelper.create_test_user(**kwargs),
                        replied_content=replied_content
                    )

                return Reply(
                    message=message,
                    creator=CreateTestUserHelper.create_test_user(**kwargs),
                    replied_content=replied_content
                )

            if "visible" in kwargs:
                visible = kwargs.pop("visible")

                if "creator" in kwargs:
                    if save:
                        return Reply.objects.create(
                            message=message,
                            creator=kwargs.pop("creator"),
                            replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse"),
                            visible=visible
                        )

                    return Reply(
                        message=message,
                        creator=kwargs.pop("creator"),
                        replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse"),
                        visible=visible
                    )
                if save:
                    return Reply.objects.create(
                        message=message,
                        creator=CreateTestUserHelper.create_test_user(**kwargs),
                        replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse"),
                        visible=visible
                    )

                return Reply(
                    message=message,
                    creator=CreateTestUserHelper.create_test_user(**kwargs),
                    replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse"),
                    visible=visible
                )

            if "creator" in kwargs:
                if save:
                    return Reply.objects.create(
                        message=message,
                        creator=kwargs.pop("creator"),
                        replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse")
                    )

                return Reply(
                    message=message,
                    creator=kwargs.pop("creator"),
                    replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse")
                )
            if save:
                return Reply.objects.create(
                    message=message,
                    creator=CreateTestUserHelper.create_test_user(**kwargs),
                    replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse")
                )

            return Reply(
                message=message,
                creator=CreateTestUserHelper.create_test_user(**kwargs),
                replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse")
            )

        else:
            cls._test_message_index = (cls._test_message_index + 1) % len(cls.TEST_MESSAGES)

            if save:
                return Reply.objects.create(
                    message=cls.TEST_MESSAGES[cls._test_message_index],
                    creator=CreateTestUserHelper.create_test_user(),
                    replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse")
                )

            return Reply(
                message=cls.TEST_MESSAGES[cls._test_message_index],
                creator=CreateTestUserHelper.create_test_user(),
                replied_content=CreateTestUserGeneratedContentHelper.create_test_user_generated_content(model="pulse")
            )

    @classmethod
    def get_test_message(cls):
        return cls.create_test_user_generated_content(model="pulse", save=False).message
