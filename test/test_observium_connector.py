import unittest
from classes.interfaces.observium_connector import ObserviumConnector
from classes import Dispatcher
from classes import Config


class TestObserviumConnector(unittest.TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'))
        self.connector = ObserviumConnector(self.dispatcher)