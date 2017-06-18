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
from classes import Device
from classes import Config
from classes import DeviceInterface
from classes import Ptr

class TestDeviceInterface(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.device = Device('localhost', Config(filename='test/configuration_examples/simple.json'))
        self.device.get_interfaces()
        for if_index, di in self.device.interfaces.iteritems():
            self.di = di
            break

    def test_add_ip_address(self):
        self.di.add_ip_address('192.0.2.1')
        self.di.add_ip_address('192.0.2.1')

    def test_get_ptr_for_ip(self):
        self.di.device.config.terse = True
        self.di.get_ptr_for_ip('192.0.2.1')
        self.di.device.config.terse = False
        self.di.get_ptr_for_ip('192.0.2.1')

    def test_get_ptrs(self):
        self.di.add_ip_address('192.0.2.x')
        self.di.get_ptrs()

    def test_ignored_interface_ptrs(self):
        self.di.ignored = True
        self.assertTrue(self.di.add_ip_address('192.0.2.1'))
        self.assertTrue(self.di.update_ptr_status('192.0.2.1', 'ptr-test.domain.example', Ptr.STATUS_UNKNOWN))
        self.di.check_ptr()
        self.assertEquals(Ptr.STATUS_UNKNOWN, self.di.get_ptrs()['192.0.2.1'].status)

    def test_ignored_ip_address_ptr(self):
        self.device.config = Config(filename='test/configuration_examples/configuration.json')
        self.assertTrue(self.di.add_ip_address('192.0.2.22'))
        self.assertTrue(self.device.config.is_ip_ignored('192.0.2.22'))
        self.di.check_ptr()

    def test_update_ptr_status(self):
        self.di.update_ptr_status('192.0.2.1', 'ptr-test.domain.example', Ptr.STATUS_NOT_CREATED)
        self.di.add_ip_address('192.0.2.1')
        self.di.update_ptr_status('192.0.2.1', 'ptr-test.domain.example', Ptr.STATUS_NOT_CREATED)

    def test_long_if_name(self):
        self.di.if_name = "Ethernet0/0/0"
        self.di._make_ptr()
        self.assertEquals('localhost-et0-0-0', self.di.ptr)
        self.di.if_name = "GigabitEthernet"
        self.di._make_ptr()

