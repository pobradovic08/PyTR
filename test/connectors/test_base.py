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


import logging
import unittest
from classes.connectors.base import BaseConnector
from classes import Dispatcher
from classes import Config
from classes import Ptr


class TestConnector(BaseConnector): pass


class TestBaseConnector(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.dispatcher = Dispatcher(
            Config(filename='test/configuration_examples/simple.json'),
            auto_load=False
        )

    def test_rasise_exception(self):
        t = TestConnector(self.dispatcher)
        self.assertRaises(NotImplementedError, t.load_ptrs)
        self.assertRaises(NotImplementedError, t.load_devices)
        self.assertRaises(NotImplementedError, t.save_ptrs, None)
        self.assertRaises(NotImplementedError, t.save_ptr, None)