from django.contrib.auth import get_user_model
from django.test import TestCase

from folioblog.user.factories import UserFactory

User = get_user_model()


class UserFactoryTestCase(TestCase):
    def setUp(self):
        UserFactory.reset_sequence()

    def test_reset_sequence(self):
        users = []
        for i in range(0, 3):
            users.append(UserFactory())
        self.assertEqual(users[0].username, "user_1")
        self.assertEqual(users[1].username, "user_2")
        self.assertEqual(users[2].username, "user_3")

        UserFactory.reset_sequence()

        users = []
        for i in range(0, 3):
            users.append(UserFactory())
        self.assertEqual(users[0].username, "user_4")
        self.assertEqual(users[1].username, "user_5")
        self.assertEqual(users[2].username, "user_6")
