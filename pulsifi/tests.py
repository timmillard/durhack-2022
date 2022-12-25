"""
    Automated test suite for pulsifi application & core.
"""

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import ManyToManyField
from django.test import TestCase

from .models import BaseUser, Profile, _Custom_Base_Model


class CreateTestProfileMixin:
    # noinspection SpellCheckingInspection
    TEST_PROFILES = [
        {"username": "padgriffin", "password": "#2@cqt", "email": "padgriffin@gmail.com"},
        {"username": "Extralas55", "password": "321321", "email": "green.anna@hotmail.co.uk"},
        {"username": "Rines1970", "password": "chicken1", "email": "robyn1973@yahoo.com"},
        {"username": "Requit", "password": "pa55word", "email": "alexander.griffiths@shaw.com"},
        {"username": "Nionothe", "password": "turnedrealizeroyal", "email": "pjackpppson@stewart.com"},
        {"username": "neha_schumm", "password": "1q2w3e4r", "email": "iyoung@gmail.com"},
        {"username": "Myseat59", "password": "password", "email": "viva_konopels@hotmail.com"},
        {"username": "Tunt1978", "password": "OoYoa9ahf", "email": "rachael2001@gmail.com"},
        {"username": "eesait4Oo", "password": "323232", "email": "julia_scott99@reynolds.com"},
        {"username": "Therhatim", "password": "JORDAN", "email": "ken80@jones.net"},
        {"username": "Repostity", "password": "aequei3Eequ", "email": "simpson.mark@clark.co.uk"},
        {"username": "Proodents445", "password": "teddybea", "email": "AlfieOsborne@dayrep.com"},
        {"username": "Hassaid", "password": "vh5150", "email": "holly65@gmail.com"},
        {"username": "alexzander", "password": "PulsifiPass123", "email": "khan.imogen@gmail.com"},
        {"username": "annalise", "password": "24101984", "email": "jessica.price@outlook.com"},
        {"username": "walter.her1992", "password": "18atcskd2w", "email": "christian40@bell.biz"},
        {"username": "rodger.nader", "password": "letmein", "email": "norene.nikola@gmail.com"},
        {"username": "lorenz._fri1988", "password": "monkey", "email": "Exielenn@studentmail.net"},
        {"username": "grayson", "password": "Iloveyou", "email": "gus2017@hotmail.com"},
        {"username": "Professor_T", "password": "lung-calf-trams", "email": "trofessor-t@trofessor-t.com"}
    ]
    TEST_BIOS = [
        "TV maven. Evil thinker. Infuriatingly humble gamer. Communicator. Pop culture advocate.",
        "The superhero movie was good but they didn't cover the part in his life where he co-founded a pizza restaurant... I assume that will be in the sequel...",
        "Just explained drain cleaning to my friend. I don't think I did it right, as she's excited to get started.",
        "Our parents blame it on the generation but do they think about who raised us.",
        "Amateurs build planes, professionals built the titanic, how do you feel now?",
        "When life gives you lemons, throw them back",
        "I saw some girl texting and driving the other day and it made me really angry. So I rolled my window down and threw my coffee at her.",
        "Liberalism is trust of the people tempered by prudence. Conservatism is distrust of the people tempered by fear.",
        "As I said before, I never repeat myself.",
        "That awkward moment when you are at a funeral and your phone rings.. your ring tone is 'I Will Survive'.",
        "Just had a beer and a taco, and now bout to finish my laundry",
        "'The best revenge is to live on and prove yourself' - Eddie Vedder",
        "Zombie trailblazer & unapologetic troublemaker.",
        "Jury duty on Monday...That in itself is a joke",
        "Love is the ultimate theme",
        "The relationship between the Prime Minister and the Head Of State",
        "Bacon fanatic",
        "My personal style is best described as 'didn't expect to have to get out of the car'",
        "Just taught my kids about taxes by eating 38% of their ice cream",
        "Haven't gotten ONE response to my hospital job applications"
    ]
    _test_profile_index = -1
    _test_bio_index = -1

    def create_test_profile(self, **kwargs):
        if kwargs:
            if ("username" not in kwargs or "password" not in kwargs or "email" not in kwargs) and "_base_user" not in kwargs:
                self._test_profile_index = (self._test_profile_index + 1) % len(self.TEST_PROFILES)

            if "_base_user" in kwargs:
                if "bio" in kwargs or "verified" in kwargs or "following" in kwargs or "visible" in kwargs or "reports" in kwargs:
                    _base_user = kwargs.pop("_base_user")
                    return Profile.objects.create(_base_user=_base_user, **kwargs)

                return Profile.objects.create(_base_user=kwargs.pop("_base_user"))

            else:
                username = self.TEST_PROFILES[self._test_profile_index]["username"]
                password = self.TEST_PROFILES[self._test_profile_index]["password"]
                email = self.TEST_PROFILES[self._test_profile_index]["email"]

                if "username" in kwargs:
                    username = kwargs.pop("username")
                if "password" in kwargs:
                    password = kwargs.pop("password")
                if "email" in kwargs:
                    email = kwargs.pop("email")

                if "bio" in kwargs or "verified" in kwargs or "visible" in kwargs:
                    if "is_superuser" in kwargs or "is_staff" in kwargs or "is_active" in kwargs:
                        base_user_kwargs = {}

                        if "is_superuser" in kwargs:
                            base_user_kwargs["is_superuser"] = kwargs.pop("is_superuser")
                        if "is_staff" in kwargs:
                            base_user_kwargs["is_staff"] = kwargs.pop("is_staff")
                        if "is_active" in kwargs:
                            base_user_kwargs["is_active"] = kwargs.pop("is_active")

                        return Profile.objects.create(
                            _base_user=BaseUser.objects.create_user(
                                username=username,
                                password=password,
                                email=email,
                                **base_user_kwargs
                            ),
                            **kwargs
                        )

                    if "visible" in kwargs:
                        is_active = kwargs.pop("visible")
                        return Profile.objects.create(
                            _base_user=BaseUser.objects.create_user(
                                username=username,
                                password=password,
                                email=email,
                                is_active=is_active
                            ),
                            **kwargs
                        )

                    return Profile.objects.create(
                        _base_user=BaseUser.objects.create_user(
                            username=username,
                            password=password,
                            email=email
                        ),
                        **kwargs
                    )

                return Profile.objects.create(
                    _base_user=BaseUser.objects.create_user(
                        username=username,
                        password=password,
                        email=email
                    )
                )

        self._test_profile_index = (self._test_profile_index + 1) % len(self.TEST_PROFILES)
        return Profile.objects.create(
            _base_user=BaseUser.objects.create_user(
                username=self.TEST_PROFILES[self._test_profile_index]["username"],
                password=self.TEST_PROFILES[self._test_profile_index]["password"],
                email=self.TEST_PROFILES[self._test_profile_index]["email"]
            )
        )

    def get_test_bio(self):
        self._test_bio_index = (self._test_bio_index + 1) % len(self.TEST_BIOS)
        return self.TEST_BIOS[self._test_bio_index]

    def get_test_unknown_field(self, field_name: str):
        print(field_name)


class GetFieldsMixin:
    def get_non_relation_fields(self, model: _Custom_Base_Model):
        return [field for field in model._meta.get_fields() if field.name != "+" and not field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, GenericRelation)]

    def get_single_relation_fields(self, model: _Custom_Base_Model):
        return [field for field in model._meta.get_fields() if field.name != "+" and field.is_relation and not isinstance(field, ManyToManyField) and not isinstance(field, GenericRelation)]

    def get_multi_relation_fields(self, model: _Custom_Base_Model):
        return [field for field in model._meta.get_fields() if field.name != "+" and (isinstance(field, ManyToManyField) or isinstance(field, GenericRelation))]


class Profile_Model_Tests(GetFieldsMixin, CreateTestProfileMixin, TestCase):
    def test_refresh_from_database_updates_non_relation_fields(self):
        profile = self.create_test_profile(bio=self.get_test_bio())
        old_profile = Profile.objects.get()

        self.assertEqual(profile, old_profile)

        for field in self.get_non_relation_fields(profile):
            self.get_test_unknown_field(field.name)
            # setattr(old_profile, field.name, )

        # self.assertNotEqual(profile.bio, old_profile.bio)

        old_profile.refresh_from_db()

    def test_stringify_displays_in_correct_format(self):
        profile = self.create_test_profile()

        self.assertEqual(str(profile), f"@{profile.base_user.username}")

        profile.update(visible=False)

        self.assertEqual(str(profile), "".join(letter + "\u0336" for letter in f"@{profile.base_user.username}"))

    def test_nonactive_base_user_makes_profile_not_visible(self):
        profile = self.create_test_profile()

        self.assertEqual(profile.base_user.is_active, True)
        self.assertEqual(profile.visible, True)

        profile.base_user.is_active = False
        profile.base_user.save()

        profile.save()

        self.assertEqual(profile.base_user.is_active, False)
        self.assertEqual(profile.visible, False)

    def test_not_visible_profile_makes_base_user_nonactive(self):
        profile = self.create_test_profile()

        self.assertEqual(profile.visible, True)
        self.assertEqual(profile.base_user.is_active, True)

        profile.update(visible=False)

        self.assertEqual(profile.visible, False)
        self.assertEqual(profile.base_user.is_active, False)
