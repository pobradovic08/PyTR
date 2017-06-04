import unittest
from classes.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config('test/configuration.json')
        self.ns_servers = ['dns1.domain.example', 'dns2.domain.example', 'dns3.domain.example', 'dns4.domain.example']
        self.ignore_rules_list = ['rule_1', 'rule_2']
        self.ignore_rules = {
            "rule_1": {
                "hostname": "hostname*"
            },
            "rule_2": {
                "hostname": "hostname*",
                "interface": "Et0/0/0"
            }
        }

        self.default_community = 'public'
        self.retries = 0
        self.timeout = 1

    def test_file_open(self):
        self.assertIsInstance(Config('test/configuration.json'), Config)
        self.assertIsInstance(Config('test/configuration_examples/simple.json'), Config)
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
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_ignore_rules(), {})

    def test_get_snmp(self):
        self.assertEquals(self.config.get_snmp_community('hostname'), self.default_community)
        self.assertEquals(self.config.get_snmp_community('1custom-host1'), self.default_community)
        self.assertEquals(self.config.get_snmp_community(), self.default_community)
        self.assertEquals(self.config.get_snmp_community('custom-host1'), 'custom_community')
        self.assertEquals(self.config.get_snmp_community('asd.domain.example'), 'custom_domain')
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_snmp_community('1custom-host1'), self.default_community)
        self.assertEquals(config.get_snmp_community('custom-host1'), self.default_community)
        self.assertEquals(config.get_snmp_community('asd.domain.example'), self.default_community)

    def test_get_snmp_retries(self):
        self.assertEquals(self.config.get_snmp_retries(), 143)
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_snmp_retries(), 0)
        self.assertEquals(config.get_snmp_retries(443), 443)