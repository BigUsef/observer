from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from django.contrib.auth import get_user_model

UserModel = get_user_model()


class TestUserModel(TestCase):
    def setUp(self) -> None:
        self.user = baker.make(
            'authentication.User',
            first_name='Mahmud',
            last_name='Youssef',
            username='bigsef',
            email='my@observer.io'
        )
        self.another_user = baker.make('authentication.User', username='7oka')

    def test_user_string_representation(self):
        self.assertEqual(str(self.another_user), '7oka')

        self.another_user.first_name = 'Youssef'
        self.another_user.last_name = 'Mahmud'
        self.assertEqual(str(self.another_user), 'Youssef Mahmud')

    def test_get_full_name(self):
        self.assertEqual(self.user.full_name, 'Mahmud Youssef')

    def test_update_last_login(self):
        old_date = timezone.now() - timezone.timedelta(days=5)

        self.user.last_login = old_date
        self.user.save()

        self.user.update_last_login(commit=False)
        self.assertEqual(self.user.last_login.minute, timezone.now().minute)
        self.assertEqual(self.user.last_login.hour, timezone.now().hour)
        self.assertEqual(self.user.last_login.day, timezone.now().day)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_login.minute, old_date.minute)
        self.assertEqual(self.user.last_login.hour, old_date.hour)
        self.assertEqual(self.user.last_login.day, old_date.day)

        self.user.update_last_login(commit=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_login.minute, timezone.now().minute)
        self.assertEqual(self.user.last_login.hour, timezone.now().hour)
        self.assertEqual(self.user.last_login.day, timezone.now().day)

    def test_generate_token(self):
        self.user.generate_token(commit=False)
        self.assertIsNotNone(self.user.token)
        self.user.refresh_from_db()
        self.assertEqual(self.user.token, '')

        self.user.generate_token(commit=True)
        self.assertIsNotNone(self.user.token)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.token)

    def test_send_user_email(self):
        # TODO: complete this test
        pass

    def test_create_super_user(self):
        users_count = UserModel.objects.count()

        created_user = UserModel.objects.create_superuser(
            username='super_user_name',
            email='super.email@observer.io',
            password='123123'
        )

        self.assertEqual(users_count + 1, UserModel.objects.count())
        self.assertTrue(created_user.is_superuser)
        self.assertTrue(created_user.is_staff)

    def test_create_regular_user(self):
        users_count = UserModel.objects.count()

        created_user = UserModel.objects.create_user(
            username='regular_user_name',
            email='regular.email@observer.io',
            password='123123'
        )

        self.assertEqual(users_count + 1, UserModel.objects.count())
        self.assertFalse(created_user.is_superuser)
        self.assertFalse(created_user.is_staff)

    def test_create_user_with_repeated_email(self):
        users_count = UserModel.objects.count()
        # TODO: complete this test

        # created_user = UserModel.objects.create_superuser(
        #     username='regular_user_name',
        #     email='my@observer.io',
        #     password='123123'
        # )

        self.assertEqual(users_count, UserModel.objects.count())

    def tearDown(self):
        UserModel.objects.all().delete()
