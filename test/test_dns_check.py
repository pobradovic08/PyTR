#!/usr/bin/python

import unittest
from classes.dns_check import DnsCheck

class TestDnsCheck(unittest.TestCase):

    def test_check_ip(self):
        self.assertTrue(DnsCheck.check_ip('109.122.98.168'))
        self.assertRaises(ValueError, DnsCheck.check_ip, '109.122.98.')
        self.assertRaises(ValueError, DnsCheck.check_ip, '109.122.98')
        self.assertRaises(ValueError, DnsCheck.check_ip, 'x.122.98.168')

    def test_ptr_query(self):
        self.assertEqual('noc.vektor.net', DnsCheck.get_ptr('109.122.98.168'))
        self.assertRaises(ValueError, DnsCheck.get_ptr_zone, '109.122.96')

    def test_get_ptr_zone(self):
        self.assertEqual('96.122.109.in-addr.arpa.', DnsCheck.get_ptr_zone('109.122.96.23'))
        self.assertRaises(ValueError, DnsCheck.get_ptr_zone, '109.122.96')

    def test_is_authoritative(self):
        self.assertTrue(DnsCheck.is_authoritative('109.122.98.168'))
        self.assertTrue(DnsCheck.is_authoritative('109.122.96.23'))
        self.assertFalse(DnsCheck.is_authoritative('89.216.119.169'))
        self.assertFalse(DnsCheck.is_authoritative('8.8.8.8'))
        self.assertFalse(DnsCheck.is_authoritative('1.1.1.1'))
        self.assertRaises(ValueError, DnsCheck.get_ptr_zone, '109.122.96')

    def test_check_status(self):
        self.assertEqual(DnsCheck.STATUS_OK, DnsCheck.get_status('91.185.98.222', 'r-sc-1.vektor.net')[1])
        self.assertEqual(DnsCheck.STATUS_NOT_UPDATED, DnsCheck.get_status('91.185.98.222', 'r-sc-1-lo0.vektor.net')[1])
        self.assertEqual(DnsCheck.STATUS_NOT_CREATED, DnsCheck.get_status('109.122.96.50', 'r-sc-1-lo0.vektor.net')[1])
        self.assertEqual(DnsCheck.STATUS_NOT_AUTHORITATIVE, DnsCheck.get_status('8.8.8.8', 'r-sc-1-lo0.vektor.net')[1])
        self.assertRaises(ValueError, DnsCheck.get_status, '109.122.96', 'r-sc-1.vektor.net')