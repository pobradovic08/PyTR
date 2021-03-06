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
from classes import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.config = Config('test/configuration_examples/configuration.json')
        self.ns_servers = [
            'localhost', 'root.localhost'
        ]
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
            "192.0.2.22",
            "1.1.1.1"
        ]

        self.default_community = 'public'
        self.retries = 0
        self.timeout = 1

    def test_file_open(self):
        self.assertIsInstance(Config('test/configuration_examples/configuration.json'), Config)
        self.assertIsInstance(Config('test/configuration_examples/simple.json'), Config)
        self.assertIsInstance(Config('test/configuration_examples/simple.json'), Config)
        self.assertRaises(IOError, Config, 'config.json')
        self.assertRaises(SystemExit, Config, 'test/configuration_examples/bad_json_file.json')

    def test_empty_config_file(self):
        # Test empty
        self.assertRaises(SystemExit, Config, 'test/configuration_examples/empty.json')

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
        config = Config('test/configuration_examples/invalid_values.json')
        self.assertFalse(config.is_device_ignored('localhost'))

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
        config = Config('test/configuration_examples/invalid_values.json')
        self.assertFalse(config.is_interface_ignored('localhost', 'interface'))

    def test_is_ip_ignored(self):
        self.assertTrue(self.config.is_ip_ignored('127.0.0.0'))
        self.assertTrue(self.config.is_ip_ignored('127.0.0.1'))
        self.assertTrue(self.config.is_ip_ignored('127.255.255.255'))
        self.assertFalse(self.config.is_ip_ignored('126.255.255.255'))
        self.assertFalse(self.config.is_ip_ignored('109.122.96.23'))
        self.assertTrue(self.config.is_ip_ignored('1.1.1.1'))
        self.assertFalse(self.config.is_ip_ignored('1.1.1.2'))
        self.assertFalse(self.config.is_ip_ignored('1.1.1.0'))

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
        config = Config('test/configuration_examples/invalid_values.json')
        self.assertEquals(config.get_snmp_retries(123), 123)
        config = Config('test/configuration_examples/invalid_values_2.json')
        self.assertEquals(config.get_snmp_retries(123), 123)

    def test_get_snmp_timeoeut(self):
        self.assertEquals(self.config.get_snmp_timeout(), 23)
        config = Config('test/configuration_examples/simple.json')
        self.assertEquals(config.get_snmp_timeout(), 1)
        self.assertEquals(config.get_snmp_timeout(443), 443)
        self.assertEquals(config.get_snmp_timeout(0.1), 0.1)
        self.assertEquals(config.get_snmp_timeout(1.9), 1.9)
        config = Config('test/configuration_examples/invalid_values.json')
        self.assertEquals(config.get_snmp_timeout(123.4), 123.4)
        config = Config('test/configuration_examples/invalid_values_2.json')
        self.assertEquals(config.get_snmp_timeout(123.4), 123.4)

    def test_get_email_server(self):
        self.assertEqual(self.config.get_email_server(), 'smtp.domain.example')

    def test_get_email_to(self):
        self.assertListEqual(self.config.get_email_to(), ["rcp@server.domain.example"])

    def test_get_email_from(self):
        self.assertEqual(self.config.get_email_from(), 'pytr@server.domain.example')
