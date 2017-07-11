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
from classes.connectors.base import BaseConnector
from classes import Dispatcher
from classes import Config
from classes import Ptr


class TestConnector(BaseConnector):
    def save_ptr(self, ptr):
        pass

    def save_ptrs(self, ptrs):
        pass

    def load_devices(self):
        return ['cmts-1.domain.example.', 'cmts-2.domain.example.', 'cmts-3.domain.example.']


class Test2Connector(BaseConnector):
    def save_ptr(self, ptr):
        pass

    def save_ptrs(self, ptrs):
        pass

    def load_devices(self):
        return ['server.domain.example.']


class Test3Connector(BaseConnector): pass


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
        # Test3 doesn't have enabled flag set. Should be ignored
        Test3Connector(self.dispatcher)
        self.assertListEqual(['TestConnector', 'Test2Connector'], self.dispatcher.get_connector_list())

    def test_connector_load(self):
        self.assertListEqual([], self.dispatcher.devices.keys())
        TestConnector(self.dispatcher)
        self.dispatcher.load()
        # No invalid hostnames included
        self.assertListEqual(
            sorted(['cmts-1.domain.example.', 'cmts-2.domain.example.']),
            sorted(self.dispatcher.devices.keys())
        )
        Test2Connector(self.dispatcher)
        self.dispatcher.load()
        # No invalid hostnames included
        self.assertListEqual(
            sorted(['cmts-1.domain.example.', 'cmts-2.domain.example.', 'server.domain.example.']),
            sorted(self.dispatcher.devices.keys())
        )

    def test_autoload(self):
        self.dispatcher = Dispatcher(
            Config(filename='test/configuration_examples/simple.json'),
            connectors_dir='/../test/connectors/modules'
        )

    def test_save_ptrs(self):
        TestConnector(self.dispatcher)
        Test2Connector(self.dispatcher)
        self.dispatcher.save_ptr(Ptr(
            ip_address=u'10.10.10.10',
            hostname='host.domain.example',
            if_name='Ethernet1/0',
            ptr='host-eth1/0.domain.example'
        ))
        self.dispatcher.save_ptrs({})

    def test_get_connector_config(self):
        connector = TestConnector(self.dispatcher)
        self.assertDictEqual(
            {
                'enabled': True
            },
            connector.config)

        dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'), auto_load=False)
        connector = TestConnector(dispatcher)
        self.assertDictEqual(
            {
                'enabled': True,
                'key': 'value'
            },
            connector.config)

        connector2 = Test2Connector(dispatcher)
        self.assertDictEqual(
            {
                'enabled': True
            },
            connector2.config)
        connector3 = Test3Connector(dispatcher)
        dispatcher.get_connector_config(connector3)
