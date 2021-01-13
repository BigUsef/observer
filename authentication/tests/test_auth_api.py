from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import reverse
from django.urls import NoReverseMatch
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class FacilityStaffAuthViewSet(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.employee = baker.make(
            'corporations.Employee',
            user__username='test_user',
            user__email='email@test.com',
            user__password='123456789',
            facility__uid='facility-test',
            facility__is_active=True,
            is_chief=True
        )
        self.employee.user.set_password('123456789')
        self.employee.user.generate_token()
        self.employee.user.save()

        self.client.credentials(
            HTTP_API_VERSION='1.1.0.0'
        )

    def test_login(self):
        api_url = reverse('auth:facility_staff-login')
        data = {
            'facility': 'facility-test',
            'username': 'test_user',
            'password': '123456789'
        }

        response = self.client.post(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.employee.user.token)
        self.assertEqual(response.data['username'], self.employee.user.username)
        self.assertEqual(response.data['full_name'], self.employee.user.full_name)

    def test_login_with_wrong_method(self):
        api_url = reverse('auth:facility_staff-login')
        data = {
            'facility': 'facility-test',
            'username': 'test_user',
            'password': '123456789'
        }

        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password(self):
        user = self.employee.user
        self.assertTrue(user.check_password('123456789'))
        self.client.credentials(
            HTTP_API_VERSION='1.1.0.0',
            HTTP_AUTHORIZATION=f'Token {user.token}'
        )

        api_url = reverse('auth:facility_staff-change-password')
        data = {'password': 'test_password'}

        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('test_password'))

    def test_change_password_with_old_pass(self):
        user = self.employee.user
        self.assertTrue(user.check_password('123456789'))
        self.client.credentials(
            HTTP_API_VERSION='1.1.0.0',
            HTTP_AUTHORIZATION=f'Token {user.token}'
        )

        api_url = reverse('auth:facility_staff-change-password')
        data = {'password': '123456789'}

        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_wrong_method(self):
        self.client.credentials(
            HTTP_API_VERSION='1.1.0.0',
            HTTP_AUTHORIZATION=f'Token {self.employee.user.token}'
        )
        api_url = reverse('auth:facility_staff-change-password')
        data = {
            'password1': 'test_password',
            'password2': 'test_password'
        }

        response = self.client.post(api_url, data, format='json')
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        facility = self.employee.facility
        self.employee.delete()
        facility.delete()


class TestUsersViewSet(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.employee = baker.make(
            'corporations.Employee',
            user__username='test_user',
            user__email='email@test.com',
            facility__uid='facility-test',
            facility__is_active=True,
            is_chief=True
        )
        self.employee.user.save()

        # related to activate account API
        self.uuid_code = uuid4()
        cache.set(self.uuid_code, {
            'id': self.employee.user.id,
            'username': self.employee.user.username,
            'email': self.employee.user.email,
            'first_name': self.employee.user.first_name,
            'last_name': self.employee.user.last_name
        })

        self.client.credentials(HTTP_API_VERSION='1.1.0.0', HTTP_ACCEPT_LANGUAGE='en')

    def test_get_activate_account_data_success(self):
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.get(api_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.employee.user.id)
        self.assertEqual(response.data['username'], self.employee.user.username)
        self.assertEqual(response.data['email'], self.employee.user.email)
        self.assertEqual(response.data['first_name'], self.employee.user.first_name)
        self.assertEqual(response.data['last_name'], self.employee.user.last_name)

    def test_activate_account_with_wrong_code_format(self):
        with self.assertRaises(NoReverseMatch) as ex:
            reverse('auth:users-activation', args=['wrongcode123wrongcode'])

    def test_activate_account_with_wrong_code(self):
        new_code = uuid4()
        api_url = reverse('auth:users-activation', args=[new_code])
        response = self.client.get(api_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_account_without_required_data(self):
        data = {
            'username': 'test_user',
            'first_name': 'User',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(all(i in response.data.keys() for i in ['last_name', 'password']))

    def test_activate_account_with_wrong_cached_data(self):
        cache.set(self.uuid_code, {
            'id': 3,
            'username': self.employee.user.username,
            'email': self.employee.user.email,
            'first_name': self.employee.user.first_name,
            'last_name': self.employee.user.last_name
        })

        data = {
            'username': 'test_user',
            'first_name': 'User',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Error in activation process, please contact', response.data)

    def test_activate_account_with_activated_user(self):
        self.employee.user.is_verified = True
        self.employee.user.save()
        data = {
            'username': 'test_user',
            'first_name': 'User',
            'last_name': 'User',
            'password': 'password',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Your account is already', response.data)

    def test_activate_account_with_wrong_username(self):
        new_user = baker.make('authentication.User')
        data = {
            'username': new_user.username,
            'first_name': 'User',
            'last_name': 'User',
            'password': 'password',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('this username belong to another user', response.data['username'])

    def test_activate_account_with_wrong_request_method(self):
        data = {
            'username': 'username',
            'first_name': 'User',
            'last_name': 'User',
            'password': 'password',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.post(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_activate_account_success_without_username(self):
        data = {
            'first_name': 'User',
            'last_name': 'User2',
            'password': 'password',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.user.username, 'test_user')
        self.assertEqual(self.employee.user.email, 'email@test.com')
        self.assertEqual(self.employee.user.first_name, 'User')
        self.assertEqual(self.employee.user.last_name, 'User2')
        self.assertTrue(self.employee.user.is_verified)
        self.assertIsNotNone(self.employee.user.token)

    def test_activate_account_success_with_username(self):
        data = {
            'username': 'username3',
            'first_name': 'User12',
            'last_name': 'User22',
            'password': 'password',
        }
        api_url = reverse('auth:users-activation', args=[self.uuid_code])
        response = self.client.put(api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.user.username, 'username3')
        self.assertEqual(self.employee.user.email, 'email@test.com')
        self.assertEqual(self.employee.user.first_name, 'User12')
        self.assertEqual(self.employee.user.last_name, 'User22')
        self.assertTrue(self.employee.user.is_verified)
        self.assertIsNotNone(self.employee.user.token)

    def tearDown(self) -> None:
        cache.delete(self.uuid_code)
        User.objects.all().delete()
        facility = self.employee.facility
        self.employee.delete()
        facility.delete()
