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


import logging
import unittest
import dns.update
from dns.tsig import HMAC_MD5

from classes import Config
from classes import Dispatcher
from classes import DnsCheck
from classes import Ptr
from classes.connectors.dns.dns_connector import DnsConnector


class TestDnsConnector(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'))
        self.connector = DnsConnector(self.dispatcher)
        self.dns = DnsCheck(config=Config('test/configuration_examples/configuration.json'))

    def test_create(self):
        ptr_dict = {
            'ip_address': u'192.0.2.255',
            'hostname': 'host255.domain.example',
            'if_name': 'Ethernet2/5/5',
            'ptr': 'host255-et2-5-5.domain.example.'
        }
        ptr = Ptr(**ptr_dict)
        self.connector.create_ptr(ptr)
        self.assertEquals('host255-et2-5-5.domain.example.', self.dns.get_ptr('192.0.2.255'))

    def test_update(self):
        ptr_dict = {
            'ip_address': u'192.0.2.255',
            'hostname': 'host255.domain.example',
            'if_name': 'Ethernet2/5/5',
            'ptr': 'host255-et2-5-5.domain.example.'
        }
        ptr = Ptr(**ptr_dict)
        self.connector.create_ptr(ptr)
        self.assertEquals('host255-et2-5-5.domain.example.', self.dns.get_ptr('192.0.2.255'))
        ptr_dict['ptr'] = 'host-et2-5-5.domain.example.'
        ptr = Ptr(**ptr_dict)
        self.connector.create_ptr(ptr)
        self.assertEquals('host-et2-5-5.domain.example.', self.dns.get_ptr('192.0.2.255'))

    def test_delete(self):
        self.connector.delete_ptr('192.0.2.255')
        self.assertNotEquals('host-et2-5-5.domain.example.', self.dns.get_ptr('192.0.2.255'))
        self.assertNotEquals('host255-et2-5-5.domain.example.', self.dns.get_ptr('192.0.2.255'))

    def test_multiple_delete(self):
        ptr1_dict = {
            'ip_address': u'192.0.2.201',
            'hostname': 'host201.domain.example',
            'if_name': 'Ethernet2/0/1',
            'ptr': 'host201-et2-0-1.domain.example.'
        }
        ptr2_dict = {
            'ip_address': u'192.0.2.202',
            'hostname': 'host202.domain.example',
            'if_name': 'Ethernet2/0/2',
            'ptr': 'host202-et2-0-2.domain.example.'
        }
        ptr3_dict = {
            'ip_address': u'192.0.2.203',
            'hostname': 'host203.domain.example',
            'if_name': 'Ethernet2/0/3',
            'ptr': 'host203-et2-0-3.domain.example.'
        }
        ptr1 = Ptr(**ptr1_dict)
        ptr2 = Ptr(**ptr2_dict)
        ptr3 = Ptr(**ptr3_dict)

        self.connector.create_ptr(ptr1)
        self.connector.create_ptr(ptr2)
        self.connector.create_ptr(ptr3)
        self.assertEquals('host201-et2-0-1.domain.example.', self.dns.get_ptr('192.0.2.201'))
        self.assertEquals('host202-et2-0-2.domain.example.', self.dns.get_ptr('192.0.2.202'))
        self.assertEquals('host203-et2-0-3.domain.example.', self.dns.get_ptr('192.0.2.203'))
        self.connector.delete_ptrs(['192.0.2.201','192.0.2.202','192.0.2.203'])
        self.assertNotEquals('host201-et2-0-1.domain.example.', self.dns.get_ptr('192.0.2.201'))
        self.assertNotEquals('host202-et2-0-2.domain.example.', self.dns.get_ptr('192.0.2.202'))
        self.assertNotEquals('host203-et2-0-3.domain.example.', self.dns.get_ptr('192.0.2.203'))