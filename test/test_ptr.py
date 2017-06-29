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

    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.ptr = {
            'ip_address': u'10.20.30.40',
            'hostname': 'cmts-sc-1.vektor.net',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'cmts-sc-1-et0-0-0.vektor.net'
        }

        self.obj = Ptr(**self.ptr)

    def test_instantiation(self):
        self.assertIsInstance(self.obj, Ptr)
        self.assertEquals(self.ptr['ip_address'], str(self.obj.ip_address))
        self.assertEquals(self.ptr['hostname'], self.obj.hostname)
        self.assertEquals(self.ptr['if_name'], self.obj.if_name)
        self.assertEquals(self.ptr['ptr'], self.obj.ptr)
        self.assertEquals(Ptr.STATUS_UNKNOWN, self.obj.status)

        self.ptr['status'] = Ptr.STATUS_IGNORED
        obj = Ptr(**self.ptr)
        self.assertEquals(Ptr.STATUS_IGNORED, obj.status)

        self.ptr['ip_address'] = 'x.x.x.x'
        self.assertRaises(ValueError, Ptr, **self.ptr)

    def test_ptr_zone(self):
        self.assertEquals('30.20.10.in-addr.arpa.', self.obj.get_ptr_zone())

    def test_ip_int(self):
        self.assertEquals(3221225985, Ptr.get_ip_int('192.0.2.1'))
        self.assertRaises(ValueError, Ptr.get_ip_int, '192.0.2.')

    def test_create_time(self):
        self.obj.create_time()

    def test_representation(self):
        self.assertEquals('cmts-sc-1-et0-0-0.vektor.net (10.20.30.40)', str(self.obj))