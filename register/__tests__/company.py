from django.test import TestCase
import json

class CompanyTest(TestCase):

    def setUp(self):
        self.company = {
            'social_name': 'Test Name',
            'name': 'Test Name',
            'client': 1,
            'city': 'Test Name',
            'found_date': '2021-11-12 10:00',
        }
    
    def test_add_company(self):
        response = self.client.post('/register/new-company/', self.company, follow=True)
        json_response = json.loads(response.content)
        print(json_response)
        self.assertTrue(response)