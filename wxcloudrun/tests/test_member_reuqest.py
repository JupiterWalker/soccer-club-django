from django.test import TestCase



class ActionQueryTestCase(TestCase):

    def test_guest_request(self):
        response = self.client.get('/get_user_info/111/', content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_apply_join_club(self):
        response = self.client.post('/apply_join_club/111/',
                                    content_type="application/json",
                                    data='{"nickname": "123456789"}')
        self.assertEqual(response.status_code, 200)