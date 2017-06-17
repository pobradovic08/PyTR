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

class TestDevice(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.device = Device('localhost', Config(filename='test/configuration_examples/simple.json'))
        self.device.get_interfaces()

    def test_get_ptrs(self):
        self.device.get_ptrs()

    def test_check_ptrs(self):
        self.device.check_ptrs()
        print self.device.get_ptrs()

    def test_get_number_of_interfaces(self):
        self.device.get_number_of_interfaces()

    def test_get_number_of_ip_addresses(self):
        self.device.get_number_of_ip_addresses()