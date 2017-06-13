# -*- coding: utf-8 -*-

import unittest
from classes import Ptr


class TestPtr(unittest.TestCase):
    def test_instantiation(self):
        ptr = {
            'ip': u'10.10.10.10',
            'device': 'cmts-sc-1.vektor.net',
            'interface': 'Ethernet0/0/0',
            'ptr': 'cmts-sc-1-et0-0-0.vektor.net'
        }

        obj = Ptr(**ptr)
        self.assertIsInstance(obj, Ptr)
        self.assertEquals(ptr['ip'], str(obj.ip))
        self.assertEquals(ptr['device'], obj.device)
        self.assertEquals(ptr['interface'], obj.interface)
        self.assertEquals(ptr['ptr'], obj.ptr)
        self.assertEquals(Ptr.STATUS_UNKNOWN, obj.status)

        ptr['status'] = Ptr.STATUS_IGNORED
        obj = Ptr(**ptr)
        self.assertEquals(Ptr.STATUS_IGNORED, obj.status)

        ptr['ip'] = 'x.x.x.x'
        self.assertRaises(ValueError, Ptr, **ptr)
