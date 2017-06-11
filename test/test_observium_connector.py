import unittest
from classes.interfaces.observium_connector import ObserviumConnector
from classes.dispatcher import Dispatcher
from classes.config import Config


class TestObserviumConnector(unittest.TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'))
        self.connector = ObserviumConnector(self.dispatcher)

    def test_test(self):
        self.assertTrue(True)