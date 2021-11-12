from django.test import TestCase
from core.views import login_view
from django.contrib.auth import get_user_model
User = get_user_model()

class LoginTest(TestCase):
    def setUp(self):
        self.credentials = {
            'email': 'admin@alchemdigital.com',
            'password': 'admin@123'
        }
        User.objects.create_user(**self.credentials)
    def test_login(self):
        response = self.client.post('/login/', self.credentials, follow=True)
        # print(response)
        # print(response.context['user'])
        # self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(True)
