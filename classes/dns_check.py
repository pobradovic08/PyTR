#-*- coding: utf-8 -*-
import socket
import re
import dns.resolver, dns.exception
import ConfigParser
import pprint

class DnsCheck:

    STATUS_UNKNOWN = 0
    STATUS_OK = 1
    STATUS_NOT_UPDATED = 2
    STATUS_NOT_CREATED = 3
    STATUS_NOT_AUTHORITATIVE = 4

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

    @staticmethod
    def get_status(ip_address, expected_ptr):
        DnsCheck.check_ip(ip_address)

        existing_ptr = DnsCheck.get_ptr(ip_address)
        if existing_ptr == ip_address:
            if DnsCheck.is_authoritative(ip_address):
                return None, DnsCheck.STATUS_NOT_CREATED
            else:
                return None, DnsCheck.STATUS_NOT_AUTHORITATIVE
        elif existing_ptr == expected_ptr:
            return existing_ptr, DnsCheck.STATUS_OK
        else:
            if DnsCheck.is_authoritative(ip_address):
                return existing_ptr, DnsCheck.STATUS_NOT_UPDATED
            else:
                return existing_ptr, DnsCheck.STATUS_NOT_AUTHORITATIVE

    @staticmethod
    def is_authoritative(ip_address):
        """
        Queries for SOA record for PTR zone and checks if mname is in servers list defined in config file
        """
        DnsCheck.check_ip(ip_address)

        # Parse config file and get list of our nameservers
        config = ConfigParser.SafeConfigParser()
        config.read('settings.cfg')
        ns_list = config.get('dns', 'servers').split(',')

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