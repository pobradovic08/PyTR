# -*- coding: utf-8 -*-
# DNS PTR updater
# Copyright (C) 2017  Pavle Obradovic (pajaja)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest
import logging
from classes import Ptr


class TestPtr(unittest.TestCase):
    def test_instantiation(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
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
