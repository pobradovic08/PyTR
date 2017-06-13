#!/usr/bin/python

import unittest

from classes import DnsCheck


class TestDnsCheck(unittest.TestCase):
    def setUp(self):
        self.dns = DnsCheck()

    def test_fqdn_query(self):
        self.assertFalse(self.dns.get_fqdn('asdasd'))
        self.assertFalse(self.dns.get_fqdn(''))
        self.assertFalse(self.dns.get_fqdn('.'))
        self.assertEquals('pavle.vektor.net', self.dns.get_fqdn('pavle'))
        self.assertEquals('cmts-sc-1.vektor.net', self.dns.get_fqdn('cmts-sc-1'))
        self.assertEquals('imap.radijusvektor.rs', self.dns.get_fqdn('imap'))

    def test_a_query(self):
        self.assertFalse(self.dns.get_a('asdasd'))
        self.assertFalse(self.dns.get_a(''))
        self.assertFalse(self.dns.get_a('.'))
        self.assertEquals('109.122.96.23', self.dns.get_a('pavle'))
        self.assertEquals('91.185.98.237', self.dns.get_a('cmts-sc-1'))
        self.assertEquals('109.122.98.37', self.dns.get_a('imap'))

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
        self.assertTrue(self.dns.is_authoritative('109.122.98.168'))
        self.assertTrue(self.dns.is_authoritative('109.122.96.23'))
        self.assertFalse(self.dns.is_authoritative('89.216.119.169'))
        self.assertFalse(self.dns.is_authoritative('8.8.8.8'))
        self.assertFalse(self.dns.is_authoritative('1.1.1.1'))

    def test_check_status(self):
        self.assertEqual(DnsCheck.STATUS_OK, self.dns.get_status('91.185.98.222', 'r-sc-1.vektor.net')[1])
        self.assertEqual(DnsCheck.STATUS_NOT_UPDATED, self.dns.get_status('91.185.98.222', 'r-sc-1-lo0.vektor.net')[1])
        self.assertEqual(DnsCheck.STATUS_NOT_CREATED, self.dns.get_status('109.122.96.50', 'r-sc-1-lo0.vektor.net')[1])
        self.assertEqual(DnsCheck.STATUS_NOT_AUTHORITATIVE, self.dns.get_status('8.8.8.8', 'r-sc-1-lo0.vektor.net')[1])
        self.assertRaises(ValueError, self.dns.get_status, '109.122.96', 'r-sc-1.vektor.net')
