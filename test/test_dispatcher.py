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
from classes.interfaces.base import BaseConnector
from classes import Dispatcher
from classes import Config


class TestConnector(BaseConnector):
    def save_ptr(self, ptr):
        pass

    def load_devices(self):
        return ['cmts-sc-1.vektor.net', 'cmts-sc-2.vektor.net', 'cmts-gs-1.vektor.net']


class Test2Connector(BaseConnector):
    def save_ptr(self, ptr):
        pass

    def load_devices(self):
        return ['noc.vektor.net']


class TestDispatcher(unittest.TestCase):
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

    def test_register_connector(self):
        self.assertListEqual([], self.dispatcher.get_connector_list())
        TestConnector(self.dispatcher)
        self.assertListEqual(['TestConnector'], self.dispatcher.get_connector_list())
        Test2Connector(self.dispatcher)
        self.assertListEqual(['TestConnector', 'Test2Connector'], self.dispatcher.get_connector_list())

    def test_connector_load(self):
        self.assertListEqual([], self.dispatcher.devices.keys())
        TestConnector(self.dispatcher)
        self.dispatcher.load()
        self.assertListEqual(
            sorted(['cmts-sc-1.vektor.net', 'cmts-sc-2.vektor.net', 'cmts-gs-1.vektor.net']),
            sorted(self.dispatcher.devices.keys())
        )
        Test2Connector(self.dispatcher)
        self.dispatcher.load()
        self.assertListEqual(
            sorted(['cmts-sc-1.vektor.net', 'cmts-sc-2.vektor.net', 'cmts-gs-1.vektor.net', 'noc.vektor.net']),
            sorted(self.dispatcher.devices.keys())
        )

    def test_get_connector_config(self):
        connector = TestConnector(self.dispatcher)
        self.assertDictEqual({}, connector.config)

        dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'))
        connector = TestConnector(dispatcher)
        self.assertDictEqual({'key': 'value'}, connector.config)

        connector2 = Test2Connector(dispatcher)
        self.assertDictEqual({}, connector2.config)
