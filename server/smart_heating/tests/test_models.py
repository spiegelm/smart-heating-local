from django.test import TestCase
from smart_heating.models import *


class ResidenceTestCase(TestCase):
    def setUp(self):
        # Residence.objects.create(rfid='3')
        pass

    def test_residence_can_be_created(self):
        """Residences can be created"""
        residence = Residence.objects.create(rfid='3')

    def test_residence_can_be_created_and_retrieved(self):
        """Residences can be created """
        residence = Residence.objects.create(rfid='3')
        self.assertEqual(residence.rfid, '3')