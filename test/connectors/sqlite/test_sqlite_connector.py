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
import time

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

    def test_load_devices(self):
        self.connector.load_devices()

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

    def test_save_ptrs(self):
        self.connector.drop_ptr_table()
        self.connector.create_ptr_table()
        ptr1 = {
            'ip_address': u'192.0.2.1',
            'hostname': 'device.domain.example',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'device-et0-0-0.domain.example'
        }
        ptr2 = {
            'ip_address': u'10.9.8.7',
            'hostname': 'host.domain.example',
            'if_name': 'Ethernet3/2/1',
            'ptr': 'host-et3-2-1.domain.example'
        }
        ptr3 = {
            'ip_address': u'192.0.2.254',
            'hostname': 'dns.domain.example',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'dns-et0-0-0.domain.example'
        }
        ptrs = {
            '192.0.2.1': Ptr(**ptr1),
            '10.9.8.7': Ptr(**ptr2),
            '192.0.2.254': Ptr(**ptr3),
        }
        # Save PTRs
        self.connector.save_ptrs(ptrs=ptrs)
        loaded_ptrs = self.connector.load_ptrs()
        # Check if IPs are the same
        self.assertListEqual(ptrs.keys(), loaded_ptrs.keys())
        # Change one of the PTRs to test updating
        ptrs['10.9.8.7'].hostname = 'changed_host.domain.example'
        # Insert again to check handling of duplicate ip keys
        self.connector.save_ptrs(ptrs=ptrs)
        loaded_ptrs = self.connector.load_ptrs()
        # Check if updated PTR record is saved to DB correctly
        self.assertEquals('changed_host.domain.example', loaded_ptrs['10.9.8.7'].hostname)

    def test_ptr_count(self):
        self.assertEquals(self.connector.ptr_count(), len(self.connector.load_ptrs()))
        ptr1 = {
            'ip_address': u'192.0.2.1',
            'hostname': 'device.domain.example',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'device-et0-0-0.domain.example'
        }
        ptr2 = {
            'ip_address': u'10.9.8.7',
            'hostname': 'host.domain.example',
            'if_name': 'Ethernet3/2/1',
            'ptr': 'host-et3-2-1.domain.example'
        }
        ptr3 = {
            'ip_address': u'192.0.2.254',
            'hostname': 'dns.domain.example',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'dns-et0-0-0.domain.example'
        }
        ptrs = {
            '192.0.2.1': Ptr(**ptr1),
            '10.9.8.7': Ptr(**ptr2),
            '192.0.2.254': Ptr(**ptr3),
        }
        # Save PTRs
        self.connector.save_ptrs(ptrs=ptrs)
        self.assertEquals(self.connector.ptr_count(), len(self.connector.load_ptrs()))

    def test_delete_ptrs(self):
        # Load one (default) ptr from database
        db_ptrs = self.connector.load_ptrs()
        # Check if there's really one
        self.assertEquals(1, len(db_ptrs))

        # Delete ptr from database
        self.connector.delete_ptrs(db_ptrs.keys())
        # Load ptrs again and check that the db is empty
        db_ptrs = self.connector.load_ptrs()
        self.assertEquals(0, len(db_ptrs))

        # Generate 256 addresses and PTRs
        tmp = [ "192.0.2.%s" % i for i in xrange(0, 256, 1)]
        ptr_dict = {}
        for ip in tmp:
            ptr_dict[ip] = Ptr(ip_address=ip, hostname='test', if_name='test', ptr='test')
        self.connector.save_ptrs(ptr_dict)
        db_ptrs = self.connector.load_ptrs()
        self.assertEquals(256, len(db_ptrs))

        ptr = {
            'ip_address': u'10.10.10.10',
            'hostname': 'cmts-sc-1.domain.example',
            'if_name': 'Ethernet0/0/0',
            'ptr': 'cmts-sc-1-et0-0-0.domain.example'
        }
        self.connector.save_ptr(Ptr(**ptr))

        db_ptrs = self.connector.load_ptrs()
        self.assertEquals(257, len(db_ptrs))

        self.connector.delete_ptrs(tmp)

        db_ptrs = self.connector.load_ptrs()
        self.assertEquals(1, len(db_ptrs))


    def test_delete_stale_ptrs(self):
        self.assertEquals(1, self.connector.ptr_count())
        ptr = {
            'ip_address': u'10.10.10.11',
            'hostname': 'cmts-sc-2.domain.example',
            'if_name': 'Ethernet0/0/1',
            'ptr': 'cmts-sc-2-et0-0-1.domain.example',
            'create_time': time.time() - 72*3600
        }
        self.connector.save_ptr(Ptr(**ptr))
        self.assertEquals(2, self.connector.ptr_count())
        self.connector.delete_stale_ptrs()
        self.assertEquals(1, self.connector.ptr_count())