from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfileTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)  # Create a user instance
        self.user.save()
        self.client.login(username=self.username, password=self.password)

    def test_user_profile(self):
        response = self.client.post(reverse('users:profile'), {'first_name': 'test', 'last_name': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user'].first_name, 'test')
        self.assertEqual(response.context['user'].last_name, 'test')
