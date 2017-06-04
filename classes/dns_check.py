#-*- coding: utf-8 -*-
import socket
import re
import dns.resolver, dns.exception
from config import Config

class DnsCheck:

    STATUS_UNKNOWN = 0
    STATUS_OK = 1
    STATUS_NOT_UPDATED = 2
    STATUS_NOT_CREATED = 3
    STATUS_NOT_AUTHORITATIVE = 4

    def __init__(self, config = None):
        self.config = config if config else Config()

    @staticmethod
    def get_fqdn(hostname):
        try:
            answers = dns.resolver.query(hostname, 'A')
            return answers.qname.to_text().rstrip('.')
        except dns.exception.DNSException:
            return False

    @staticmethod
    def get_a(hostname):
        try:
            answers = dns.resolver.query(hostname, 'A')
            for rdata in answers:
                return rdata.to_text()
        except dns.exception.DNSException:
            return False

    @staticmethod
    def get_ptr(ip_address):
        DnsCheck.check_ip(ip_address)
        return socket.getfqdn(ip_address)

    def get_status(self, ip_address, expected_ptr):
        """
        Checks if expected and existing PTR for the IP address are the same.
        There are 3 statuses returned:
            - DnsCheck.STATUS_OK:                   Existing PTR is the same as expected one
            - DnsCheck.STATUS_NOT_UPDATED:          Existing PTR is not the same as expected one
            - DnsCheck.STATUS_NOT_CREATED:          There is no existing PTR
            - DnsCheck.STATUS_NOT_AUTHORITATIVE:    PTR not OK but we don't control the DNS server

        :param ip_address:      IP address to check
        :param expected_ptr:    Expected PTR for provided IP address
        :return:
        """
        DnsCheck.check_ip(ip_address)
        existing_ptr = DnsCheck.get_ptr(ip_address)
        # There is no PTR
        if existing_ptr == ip_address:
            # Are we responsible for that PTR zone?
            if self.is_authoritative(ip_address):
                return None, DnsCheck.STATUS_NOT_CREATED
            else:
                return None, DnsCheck.STATUS_NOT_AUTHORITATIVE
        # PTR is the same as expected one
        elif existing_ptr == expected_ptr:
            return existing_ptr, DnsCheck.STATUS_OK
        # PTR differs from expected one
        else:
            # Are we responsible for that PTR zone?
            if self.is_authoritative(ip_address):
                return existing_ptr, DnsCheck.STATUS_NOT_UPDATED
            else:
                return existing_ptr, DnsCheck.STATUS_NOT_AUTHORITATIVE

    def is_authoritative(self, ip_address):
        """
        Checks if we are responsible for PTR zone.
        Queries for SOA record for PTR zone and checks if mname is in servers list defined in config file
        """
        DnsCheck.check_ip(ip_address)
        ns_list = self.config.get_ns_servers()

        # Get SOA record. If master name is in ns servers list return true
        try:
            answers = dns.resolver.query(DnsCheck.get_ptr_zone(ip_address), 'SOA')
            for rdata in answers:
                # Remove fqdn dot from the end of the master name in SOA and check if in our NS servers list
                if str(rdata.mname).rstrip('.') in ns_list:
                    return True
        except dns.exception.DNSException:
            return False
        return False

    @staticmethod
    def get_ptr_zone(ip_address):
        """ Returns ptr zone in x.y.z.in-addr.arpa format """
        DnsCheck.check_ip(ip_address)
        # Get first 3 octets, reverse them and append '.in-addr.arpa.'
        parts = ip_address.split('.')
        zone = '.'.join(list(reversed(parts[:-1]))) + '.in-addr.arpa.'
        return zone

    @staticmethod
    def check_ip(ip_address):
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address):
            raise ValueError('IP address format not valid')
        else:
            return True