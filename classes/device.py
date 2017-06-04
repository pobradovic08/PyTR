# -*- coding: utf-8 -*-
import re, sre_constants

import easysnmp
from device_interface import DeviceInterface
from dns_check import DnsCheck
from config import Config
import ConfigParser


class Device:
    def __init__(self, hostname, community):
        self.hostname = DnsCheck.get_fqdn(hostname)
        if not self.hostname:
            self.hostname = hostname
        self.ip = DnsCheck.get_a(self.hostname)
        self.community = community
        self.interfaces = {}
        self.ignored = False

        configuration = Config()
        ignore_rules = configuration.get_ignore_rules()

        for rule_name, rule in ignore_rules.iteritems():
            try:
                if re.match(rule['hostname'], self.hostname):
                    self.ignored = True
            except sre_constants.error:
                #TODO: Real logging, not this shit
                print "Rule '%s' in configuration file invalid, skipping..." % rule_name

    def get_interfaces(self):
        if self.ignored:
            return True
        try:
            session = easysnmp.Session(
                hostname=self.hostname,
                community=self.community,
                use_numeric=True,
                version=2,
                timeout=1,
                retries=0
            )

            oid_pattern = re.compile(r"\.1\.3\.6\.1\.2\.1\.4\.20\.1\.2\.")

            interface_addresses_result = session.walk('.1.3.6.1.2.1.4.20.1.2')
            for interface_address_result in interface_addresses_result:
                ifIndex = int(interface_address_result.value)
                if ifIndex not in self.interfaces:
                    self.interfaces[ifIndex] = DeviceInterface(self, ifIndex)


                # Remove the part of the OID we used to walk on. Leave just the IP address part.
                ip_address = '.'.join([
                    re.sub(oid_pattern, '', interface_address_result.oid),
                    interface_address_result.oid_index
                ])
                self.interfaces[ifIndex].add_ip_address(ip_address)

            return True
        except easysnmp.EasySNMPError:
            return False

    def check_ptrs(self):
        for interface in self.interfaces:
            for ip_address in self.interfaces[interface].ip_addresses:
                if ip_address == self.ip:
                    existing_ptr, status = DnsCheck.get_status(ip_address, self.hostname)
                else:
                    existing_ptr, status = DnsCheck.get_status(ip_address, self.interfaces[interface].ptr)
                self.interfaces[interface].update_ptr_status(ip_address, existing_ptr, status)

    def __repr__(self):
        str = '═' * 97 + "\n"
        if self.ignored:
            str += "\n\033[93m\033[07m\033[04m DEVICE ON IGNORE LIST \033[0m\n\n"
        str += "\033[01mDevice:\t\t%s\n" % self.hostname
        str += "Interfaces:\t%d\n\033[0m" % len(self.interfaces)
        if len(self.interfaces):
            str += '━' * 97 + "\n"
            str += "%-9s %-26s %-44s %s\n" % ('ifIndex', 'ifName', 'PTR', 'IP address')
            str += '─' * 97  + "\n"
            for interface in self.interfaces:
                str += self.interfaces[interface].__repr__()
                str += "\033[90m" + '┈' * 97 + "\033[0m\n"
        str += '═' * 97  + "\n"
        return str