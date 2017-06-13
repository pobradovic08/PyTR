# -*- coding: utf-8 -*-
import unittest
import logging
from classes.interfaces.observium_connector import ObserviumConnector
from classes import Dispatcher
from classes import Config


class TestObserviumConnector(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'))
        self.connector = ObserviumConnector(self.dispatcher)
