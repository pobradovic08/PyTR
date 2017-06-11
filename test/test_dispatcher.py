#!/usr/bin/python

import unittest
from classes.interfaces.base_connector import BaseConnector
from classes.dispatcher import Dispatcher
from classes.config import Config


class TestConnector(BaseConnector):
    def load_devices(self):
        return ['cmts-sc-1.vektor.net', 'cmts-sc-2.vektor.net', 'cmts-gs-1.vektor.net']

class Test2Connector(BaseConnector):
    def load_devices(self):
        return ['noc.vektor.net']


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = Dispatcher(Config(filename='test/configuration_examples/simple.json'))

    def test_register_connector(self):
        self.assertListEqual([], self.dispatcher.get_connector_list())
        connector = TestConnector(self.dispatcher)
        self.assertListEqual(['TestConnector'], self.dispatcher.get_connector_list())
        connector2 = Test2Connector(self.dispatcher)
        self.assertListEqual(['TestConnector', 'Test2Connector'], self.dispatcher.get_connector_list())

    def test_connector_load(self):
        self.assertListEqual([], self.dispatcher.devices.keys())
        connector = TestConnector(self.dispatcher)
        self.dispatcher.load()
        self.assertListEqual(
            sorted(['cmts-sc-1.vektor.net', 'cmts-sc-2.vektor.net', 'cmts-gs-1.vektor.net']),
            sorted(self.dispatcher.devices.keys())
        )
        connector2 = Test2Connector(self.dispatcher)
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

