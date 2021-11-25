from django.test import TestCase

class RegisterTest(TestCase):

    def setUp(self):
        self.user = {
            'first_name': 'Bairavan',
            'last_name': 'Durairaj',
            'email': 'bairavan@alchemdigital.com',
            'password1': 'myPass#1996',
        }
    
    def test_register(self):
        response = self.client.post('/register/admin/', self.user, follow=True)
        self.assertRedirects(response, '/dashboard/', status_code=302, target_status_code=200, fetch_redirect_response=True)
