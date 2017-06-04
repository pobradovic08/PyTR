import unittest
from classes.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config('test/configuration.json')
        self.ns_servers = ['ns1.vektor.net', 'ns2.vektor.net', 'ns3.vektor.net', 'ns4.vektor.net']
        self.ignore_rules_list = ['rule_1', 'rule_2']
        self.ignore_rules = {
            "rule_1": {
                "hostname": "lb-node*"
            },
            "rule_2": {
                "hostname": "cmts*",
                "interface": "Et0/0/0"
            }
        }

    def test_file_open(self):
        self.assertIsInstance(Config('test/configuration.json'), Config)
        self.assertIsInstance(Config(), Config)
        self.assertRaises(IOError, Config, 'config.json')
        self.assertRaises(ValueError, Config, 'test/bad_json_file.json')

    def test_get_ns_list(self):
        self.assertListEqual(self.config.data['dns']['servers'], self.ns_servers)
        self.assertListEqual(self.config.get_ns_servers(), self.ns_servers)

    def test_get_ignore(self):
        self.assertListEqual(self.config.data['ignore'].keys(), self.ignore_rules_list)
        self.assertListEqual(self.config.get_ignore_rules().keys(), self.ignore_rules_list)
        self.assertEquals(self.config.get_ignore_rules(), self.ignore_rules)
