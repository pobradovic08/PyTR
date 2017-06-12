#-*- coding: utf-8 -*-

import unittest
from classes.ptr import Ptr

class TestPtr(unittest.TestCase):

    def test_instantiation(self):
        ptr_ok = {
            'ip': '10.10.10.10',
            'device': 'cmts-sc-1.vektor.net',
            'interface': 'Ethernet0/0/0',
            'ptr': 'cmts-sc-1-et0-0-0.vektor.net'
        }

        self.assertIsInstance(Ptr(**ptr_ok), Ptr)
