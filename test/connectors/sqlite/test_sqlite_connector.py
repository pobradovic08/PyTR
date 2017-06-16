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
import sqlite3

from classes import Config
from classes import Dispatcher
from classes import Ptr
from classes.connectors.sqlite.sqlite_connector import SqliteConnector


class TestSqliteConnector(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='test/unittest.log',
            format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
            level=logging.DEBUG,
            filemode='w'
        )
        self.dispatcher = Dispatcher(Config(filename='test/configuration_examples/configuration.json'))
        self.connector = SqliteConnector(self.dispatcher)
        self.connector.create_ptr_table()
        ptr = {
            'ip_address': u'10.10.10.10',
            'hostname': 'cmts-sc-1.domain.example',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'cmts-sc-1-et0-0-0.domain.example'
        }
        self.connector.save_ptr(Ptr(**ptr))

    def tearDown(self):
        self.connector.drop_ptr_table()

    def test_load_ptrs(self):
        ptrs = self.connector.load_ptrs()
        self.assertEquals(1, len(ptrs))
        self.assertListEqual(['10.10.10.10'], [str(x) for x in ptrs.keys()])
        self.assertEquals('10.10.10.10', str(ptrs['10.10.10.10'].ip_address))
        self.assertEquals('cmts-sc-1.domain.example', ptrs['10.10.10.10'].hostname)
        self.assertEquals('Ethernet0/0/0', ptrs['10.10.10.10'].if_name)
        self.assertEquals('cmts-sc-1-et0-0-0.domain.example', ptrs['10.10.10.10'].ptr)
        self.assertEquals('10.10.10.in-addr.arpa.', ptrs['10.10.10.10'].get_ptr_zone())



    def test_drop_ptr_table(self):
        self.connector.drop_ptr_table()
        self.assertRaises(sqlite3.OperationalError, self.connector.load_ptrs)
