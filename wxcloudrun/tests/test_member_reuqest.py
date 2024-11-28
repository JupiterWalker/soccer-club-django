import json

from django.test import TestCase



class ActionQueryTestCase(TestCase):

    def test_guest_request(self):
        response = self.client.get('/get_user_info/', content_type="application/json", headers={"X-Wx-openid" :"111"})
        self.assertEqual(response.status_code, 200)

    def test_apply_join_club(self):
        response = self.client.post('/apply_join_club/',
                                    content_type="application/json", headers={"X-Wx-openid" :"111"},
                                    data='{"nickname": "123456789"}')
        self.assertEqual(response.status_code, 200)

    def test_get_user_detail_info(self):
        response = self.client.post('/apply_join_club/',
                                    content_type="application/json", headers={"X-Wx-openid": "111"},
                                    data='{"nickname": "123456789", "avatar": "avatar_url"}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/get_personal_charge_info_and_activity_history/',
                                    content_type="application/json", headers={"X-Wx-openid" :"111"})
        self.assertEqual(response.status_code, 200)

    def test_set_user_info(self):
        response = self.client.put('/set_user_info/',
                                    content_type="application/json", headers={"X-Wx-openid" :"111"},
                                    data='{"avatar": "avatar:123456789"}')
        self.assertEqual(response.status_code, 200)

    def test_create_activity(self):
        response = self.client.post('/activity/',
                                    content_type="application/json", headers={"X-Wx-openid" :"111"},
                                    data=json.dumps({"location": "location", "datetime": "2024-11-11 10:10:10.23123",
                                                     "type": "match", "comment": "comment", "headcount": 10, "latitude": 1.0, "longitude": 1.0}))
        self.assertEqual(response.status_code, 200)