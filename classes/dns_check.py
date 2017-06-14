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


import socket
import dns.resolver
import dns.exception
import logging
import ipaddress
from config import Config


class DnsCheck:
    STATUS_UNKNOWN = 0
    STATUS_OK = 1
    STATUS_NOT_UPDATED = 2
    STATUS_NOT_CREATED = 3
    STATUS_NOT_AUTHORITATIVE = 4
    STATUS_IGNORED = 5

    def __init__(self, config=None):
        self.logger = logging.getLogger('dns_update.dns_check')
        self.config = config if config else Config()
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = self.config.get_ns_search_servers()
        self.logger.info("There are %d NS server(s) to query" % len(self.resolver.nameservers))
        self.resolver.search = []
        for domain in self.config.get_ns_search_domains():
            self.resolver.search.append(dns.name.from_text(domain))
        self.logger.info("There are %d domains in search list" % len(self.resolver.search))

    def get_fqdn(self, hostname):
        if not len(hostname):
            self.logger.debug("Empty hostname provided")
            return False
        try:
            answers = self.resolver.query(hostname, 'A')
            fqdn = answers.qname.to_text().rstrip('.')
            self.logger.debug("FQDN for '%s' is '%s'" % (hostname, fqdn))
            return fqdn
        except dns.exception.DNSException as e:
            self.logger.error("DNSException raised for '%s': %s" % (hostname, e))
            return False

    def get_a(self, hostname):
        if not len(hostname):
            self.logger.debug("Empty hostname provided")
            return False
        try:
            answers = self.resolver.query(hostname, 'A')
            for rdata in answers:
                ip = rdata.to_text()
                self.logger.debug("IP for '%s' is '%s'" % (hostname, ip))
                return ip
        except dns.exception.DNSException as e:
            self.logger.error("DNSException raised for '%s': %s" % (hostname, e))
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
            - DnsCheck.STATUS_IGNORED:              Interface or IP ignored

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
                self.logger.info("PTR for '%s' doesn't exists and should be created. Returning status %d" % (
                    ip_address,
                    DnsCheck.STATUS_NOT_CREATED
                ))
                return None, DnsCheck.STATUS_NOT_CREATED
            else:
                self.logger.debug("No PTR for '%s' and We're not responsible for it. Returning status %d" % (
                    ip_address,
                    DnsCheck.STATUS_NOT_AUTHORITATIVE
                ))
                return None, DnsCheck.STATUS_NOT_AUTHORITATIVE
        # PTR is the same as expected one
        elif existing_ptr == expected_ptr:
            self.logger.debug("PTR for '%s' points to %s. Status OK (%d)" % (
                ip_address,
                existing_ptr,
                DnsCheck.STATUS_NOT_AUTHORITATIVE
            ))
            return existing_ptr, DnsCheck.STATUS_OK
        # PTR differs from expected one
        else:
            # Are we responsible for that PTR zone?
            if self.is_authoritative(ip_address):
                self.logger.debug("PTR for '%s' points to %s. Update to '%s'. Status (%d)" % (
                    ip_address,
                    existing_ptr,
                    expected_ptr,
                    DnsCheck.STATUS_NOT_AUTHORITATIVE
                ))
                return existing_ptr, DnsCheck.STATUS_NOT_UPDATED
            else:
                self.logger.debug("PTR for '%s' points to '%s'. We're not responsible for it. Returning status %d" % (
                    ip_address,
                    existing_ptr,
                    DnsCheck.STATUS_NOT_AUTHORITATIVE
                ))
                return existing_ptr, DnsCheck.STATUS_NOT_AUTHORITATIVE

    def is_authoritative(self, ip_address):
        """
        Checks if we are responsible for PTR zone.
        Queries for SOA record for PTR zone and checks if mname is in servers list defined in config file
        """
        DnsCheck.check_ip(ip_address)
        ns_list = self.config.get_ns_servers()

        # Get SOA record. If master name is in ns servers list return true
        ptr_zone = DnsCheck.get_ptr_zone(ip_address)
        try:
            answers = dns.resolver.query(ptr_zone, 'SOA')
            for rdata in answers:
                # Remove fqdn dot from the end of the master name in SOA and check if in our NS servers list
                if str(rdata.mname).rstrip('.') in ns_list:
                    self.logger.debug("Server responsible for '%s' is in NS list" % ip_address)
                    return True
        except dns.exception.DNSException as e:
            self.logger.warning("Error querying '%s' SOA RR: %s" % (ptr_zone, e))
            return False

        self.logger.debug("Server responsible for '%s' is NOT in NS list" % ip_address)
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
    # TODO: replace with real check from ipaddress module
    def check_ip(ip_address):
        try:
            ipaddress.IPv4Network(unicode(ip_address))
            return True
        except ipaddress.AddressValueError:
            raise ValueError("IP address '%s' is invalid" % ip_address)
