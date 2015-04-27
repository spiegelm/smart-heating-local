from rest_framework.test import APITestCase
from smart_heating import models


class ViewRootTestCase(APITestCase):

    def test_root_contains_residence_url(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {'residence': 'http://testserver/residence/'})


class ViewResidenceTestCase(APITestCase):

    def test_get_empty_residence_list(self):
        response = self.client.get('/residence/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_nonempty_residence_list(self):
        residence = models.Residence.objects.create(rfid='3')
        response = self.client.get('/residence/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data.get('rfid'), '3', 'RFID')
        self.assertEqual(data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(data.get('room_base_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(data.get('rooms'), [])

    def test_get_residence_detail_without_rooms(self):
        residence = models.Residence.objects.create(rfid='3')
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data.get('rfid'), '3', 'RFID')
        self.assertEqual(data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(data.get('room_base_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(data.get('rooms'), [])

    def test_get_residence_detail_with_rooms(self):
        residence = models.Residence.objects.create(rfid='3')
        room1 = models.Room.objects.create(residence=residence)
        room2 = models.Room.objects.create(residence=residence)
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data.get('rfid'), '3', 'RFID')
        self.assertEqual(data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(data.get('room_base_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(data.get('rooms'), [room1.pk, room2.pk])

    # TODO add test for PUT and POST

class ViewRoomTestCase(APITestCase):

    residence = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')

    def test_get_empty_room_list(self):
        response = self.client.get('/residence/3/room/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_nonempty_room_list(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        response = self.client.get('/residence/3/room/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data.get('name'), 'Dining Room')
        self.assertEqual(data.get('residence'), 'http://testserver/residence/3/')

    # TODO add test for PUT and POST
