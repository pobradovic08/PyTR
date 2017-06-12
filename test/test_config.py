import unittest
import ipaddress
from classes import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config('test/configuration_examples/configuration.json')
        self.ns_servers = ['dns1.domain.example', 'dns2.domain.example', 'dns3.domain.example', 'dns4.domain.example']
        self.ignore_rules_list = sorted(['lb-node.*', 'cmts.*', 'rfgw.*', 'test', 'xxx'])
        self.ignore_rules = {
            "test": [],
            "lb-node.*": [],
            "rfgw.*": [],
            "cmts.*": [
                "Et0/0/0"
            ],
            "xxx": [
                "eth0",
                "eth1",
                "eth2.*"
            ]
        }
        self.ip_ignore_rules = [
            "127.0.0.0/8",
            "256.0.0.0",
            "109.0.0.0/33",
            "1.1.1.1"
        ]

        self.default_community = 'public'
        self.retries = 0
        self.timeout = 1

    def test_file_open(self):
        self.assertIsInstance(Config('test/configuration_examples/configuration.json'), Config)
        self.assertIsInstance(Config('test/configuration_examples/simple.json'), Config)
        self.assertIsInstance(Config(), Config)
        self.assertRaises(IOError, Config, 'config.json')
        self.assertRaises(ValueError, Config, 'test/configuration_examples/bad_json_file.json')

    def test_get_ns_list(self):
        self.assertListEqual(self.config.data['dns']['servers'], self.ns_servers)
        self.assertListEqual(self.config.get_ns_servers(), self.ns_servers)

    def test_get_device_ignored(self):
        self.assertListEqual(sorted(self.config.data['ignored']['device'].keys()), self.ignore_rules_list)
        self.assertListEqual(sorted(self.config.get_device_ignore_rules().keys()), self.ignore_rules_list)
        self.assertEquals(self.config.get_device_ignore_rules(), self.ignore_rules)
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_device_ignore_rules(), {})

    def test_get_ip_ignored(self):
        self.assertListEqual(sorted(self.ip_ignore_rules), sorted(self.config.data['ignored']['ip']))
        self.assertListEqual(sorted(self.ip_ignore_rules), sorted(self.config.get_ip_ignore_rules()))
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_ip_ignore_rules(), [])

    def test_is_device_ignored(self):
        self.assertTrue(self.config.is_device_ignored('lb-node1.vektor.net'))
        self.assertFalse(self.config.is_device_ignored('cmts-sc-1.vektor.net'))
        self.assertTrue(self.config.is_device_ignored('test'))
        self.assertFalse(self.config.is_device_ignored('test1'))
        self.assertFalse(self.config.is_device_ignored('1test'))
        self.assertFalse(self.config.is_device_ignored(''))

    def test_is_interface_ignored(self):
        self.assertTrue(self.config.is_interface_ignored('lb-node1.vektor.net', 'eth0'))
        self.assertTrue(self.config.is_interface_ignored('cmts-sc-1.vektor.net', 'Et0/0/0'))
        self.assertFalse(self.config.is_interface_ignored('cmts-sc-1.vektor.net', 'Et1/0/0'))
        self.assertFalse(self.config.is_interface_ignored('cmts-sc-1.vektor.net', 'Et0/0/01'))
        self.assertFalse(self.config.is_interface_ignored('cmts-sc-1.vektor.net', '0Et0/0/0'))
        self.assertFalse(self.config.is_interface_ignored('cmts-sc-1.vektor.net', ''))
        self.assertTrue(self.config.is_interface_ignored('xxx', 'eth0'))
        self.assertTrue(self.config.is_interface_ignored('xxx', 'eth0'))
        self.assertTrue(self.config.is_interface_ignored('xxx', 'eth2'))
        self.assertTrue(self.config.is_interface_ignored('xxx', 'eth21'))
        self.assertFalse(self.config.is_interface_ignored('xxx', 'eth01'))
        self.assertFalse(self.config.is_interface_ignored('xxx', '1eth0'))
        self.assertTrue(self.config.is_interface_ignored('test', 'ethasdasd'))

    def test_is_ip_ignored(self):
        self.assertTrue(self.config.is_ip_ignored(u'127.0.0.0'))
        self.assertTrue(self.config.is_ip_ignored(u'127.0.0.1'))
        self.assertTrue(self.config.is_ip_ignored(u'127.255.255.255'))
        self.assertFalse(self.config.is_ip_ignored(u'126.255.255.255'))
        self.assertFalse(self.config.is_ip_ignored(u'109.122.96.23'))
        self.assertTrue(self.config.is_ip_ignored(u'1.1.1.1'))
        self.assertFalse(self.config.is_ip_ignored(u'1.1.1.2'))
        self.assertFalse(self.config.is_ip_ignored(u'1.1.1.0'))


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
        self.assertEquals(config.get_snmp_retries(1.0), 1)
        self.assertEquals(config.get_snmp_retries(1.9), 1)
        self.assertEquals(config.get_snmp_retries(2.4), 2)
        self.assertRaises(ValueError, config.get_snmp_retries, 'asd')
        self.assertRaises(ValueError, config.get_snmp_retries, -1)

    def test_get_snmp_timeoeut(self):
        self.assertEquals(self.config.get_snmp_timeout(), 23)
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_snmp_timeout(), 1)
        self.assertEquals(config.get_snmp_timeout(443), 443)
        self.assertEquals(config.get_snmp_timeout(0.1), 0.1)
        self.assertEquals(config.get_snmp_timeout(1.9), 1.9)
        self.assertRaises(ValueError, config.get_snmp_timeout, 'asd')
        self.assertRaises(ValueError, config.get_snmp_timeout, -1)
        self.assertRaises(ValueError, config.get_snmp_timeout, 0)
        self.assertRaises(ValueError, config.get_snmp_timeout, 0.0)