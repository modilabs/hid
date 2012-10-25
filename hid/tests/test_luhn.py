from django.conf import settings
from django.test import TestCase
from hid.utils import *


class LuhnTest(TestCase):

    def setUp(self):
        ''' Test Luhn Using mod n'''

    def test_checkDigit(self):
        ''' Test check digit '''
