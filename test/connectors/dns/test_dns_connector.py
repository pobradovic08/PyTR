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

    def test_update(self):
        update = dns.update.Update('2.0.192.in-addr.arpa', keyring=self.connector.keyring, keyalgorithm=HMAC_MD5)
        update.replace('255', 300, 'PTR', '255-test.domain.example.')
        dns.query.tcp(update, 'localhost')
        self.assertEquals('255-test.domain.example.', self.dns.get_ptr('192.0.2.255'))
