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
import ipaddress
from classes import DnsCheck
from classes import Config


class TestDnsCheck(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.dns = DnsCheck(config=Config('test/configuration_examples/configuration.json'))

    def test_fqdn_query(self):
        self.assertFalse(self.dns.get_fqdn('asdasd'))
        self.assertFalse(self.dns.get_fqdn(''))
        self.assertFalse(self.dns.get_fqdn('.'))
        self.assertEquals('host1.domain.example', self.dns.get_fqdn('host1'))
        self.assertEquals('host2.domain.example', self.dns.get_fqdn('host2'))
        self.assertEquals('host3.domain.example', self.dns.get_fqdn('host3'))

    def test_a_query(self):
        self.assertFalse(self.dns.get_a('asdasd'))
        self.assertFalse(self.dns.get_a(''))
        self.assertFalse(self.dns.get_a('.'))
        self.assertEquals('192.0.2.1', self.dns.get_a('host1'))
        self.assertEquals('192.0.2.2', self.dns.get_a('host2'))
        self.assertEquals('192.0.2.3', self.dns.get_a('host3'))

    def test_ptr_query(self):
        self.assertRaises(ipaddress.AddressValueError, self.dns.get_ptr, 'x.x.x.x')
        self.assertEquals('host1.domain.example.', self.dns.get_ptr('192.0.2.1'))
        self.assertEquals('host2.domain.example.', self.dns.get_ptr('192.0.2.2'))
        self.assertEquals('host3.domain.example.', self.dns.get_ptr('192.0.2.3'))
        self.assertRaises(ValueError, DnsCheck.get_ptr_zone, '192.0.2')

    def test_get_ptr_zone(self):
        self.assertRaises(ipaddress.AddressValueError, DnsCheck.get_ptr_zone, 'x.x.x.x')
        self.assertEqual('2.0.192.in-addr.arpa.', DnsCheck.get_ptr_zone('192.0.2.1'))
        self.assertRaises(ValueError, DnsCheck.get_ptr_zone, '192.0.2')

    def test_is_authoritative(self):
        self.assertRaises(ipaddress.AddressValueError, self.dns.is_authoritative, 'x.x.x.x')
        self.assertTrue(self.dns.is_authoritative('192.0.2.1'))
        self.assertTrue(self.dns.is_authoritative('192.0.2.255'))
        self.assertFalse(self.dns.is_authoritative('89.216.119.169'))
        self.assertFalse(self.dns.is_authoritative('109.122.98.1'))
        self.assertFalse(self.dns.is_authoritative('1.1.1.1'))

    def test_check_status(self):
        self.assertRaises(ipaddress.AddressValueError, self.dns.get_status, 'x.x.x.x', 'test')
        # OK PTR
        self.assertEqual(DnsCheck.STATUS_OK,
                         self.dns.get_status('192.0.2.1', 'host1.domain.example.')[1])
        # Authoritative
        # Wrong PTR
        self.assertEqual(DnsCheck.STATUS_NOT_UPDATED,
                         self.dns.get_status('192.0.2.22', 'localhost.domain.example.')[1])
        # No PTR
        self.assertEqual(DnsCheck.STATUS_NOT_CREATED,
                         self.dns.get_status('192.0.2.4', 'host4.domain.example.')[1])
        # Not authoritative
        # Wrong PTR
        self.assertEqual(DnsCheck.STATUS_NOT_AUTHORITATIVE,
                         self.dns.get_status('8.8.8.8', 'wrong.domain.example.')[1])
        # No PTR
        self.assertEqual(DnsCheck.STATUS_NOT_AUTHORITATIVE,
                         self.dns.get_status('8.8.8.255', 'empty.domain.example.')[1])

        # Wrong IP
        self.assertRaises(ValueError, self.dns.get_status, '192.0.2', 'something.domain.example.')
