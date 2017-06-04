# -*- coding: utf-8 -*-
import re, sre_constants

import easysnmp
from device_interface import DeviceInterface
from dns_check import DnsCheck
from config import Config


class Device:

    def __init__(self, hostname, config):
        """
        Initialize instance with empty interfaces array
        :param hostname:    Hostname of device. If it's not FQDN we will try to resolve to one
        :param config:      Config instance
        """

        self.config = config
        self.interfaces = {}
        self.ignored = False

        # Try to get FQDN for the hostname
        # If it fails, use provided hostname
        self.hostname = DnsCheck.get_fqdn(hostname)
        if not self.hostname:
            self.hostname = hostname

        # Get IN A record for device hostname
        self.ip = DnsCheck.get_a(self.hostname)

        # TODO: update to support v3
        self.community = config.get_snmp_community(self.hostname)

        # Configuration
        configuration = Config()
        ignore_rules = configuration.get_ignore_rules()

        # Go trough each ignore rule and check
        # if the hostname regexp matches device hostname
        for rule_name, rule in ignore_rules.iteritems():
            try:
                if re.match(rule['hostname'], self.hostname):
                    self.ignored = True
            except sre_constants.error:
                #TODO: Real logging, not this shit
                print "Rule '%s' in configuration file invalid, skipping..." % rule_name

    def get_interfaces(self):
        """
        Walks trough the
        and fetches IP address and  IF-MIB::ifIndex
        :return:
        """

        # If device is on ignore list skip interface discovery
        # Interfaces dictionary will be empty
        if self.ignored:
            return True

        #TODO: Use settings from Config
        # Setup SNMP session
        try:
            self.session = easysnmp.Session(
                hostname=self.hostname,
                community=self.community,
                use_numeric=True,
                version=2,
                timeout=1,
                retries=self.config.get_snmp_retries()
            )

            """
            Implemented OID IP-MIB::ipAdEntIfIndex (1.3.6.1.2.1.4.20.1.2) is apparently deprecated.
            The new IP-MIB::ipAddressIfIndex is not implemented on most network devices.
            """

            # Compiled regexp pattern - ipAdEntIfIndex + important dot ;)
            oid_pattern = re.compile(re.escape('.1.3.6.1.2.1.4.20.1.2.'))

            # Walk trough the IP-MIB::ipAdEntIfIndex tree. Results are in format:
            # .1.3.6.1.2.1.4.20.1.2.10.170.0.129 = INTEGER: 8
            # .1.3.6.1.2.1.4.20.1.2.10.170.1.1 = INTEGER: 10
            #       OID ends here-^|^- IP starts here     ^- ifIndex
            # etc...
            interface_addresses_result = self.session.walk('.1.3.6.1.2.1.4.20.1.2')
            for interface_address_result in interface_addresses_result:

                # IF-MIB::ifIndex later used to get IF-MIB::ifName
                ifIndex = int(interface_address_result.value)
                # If this is the first time encountering this ifIndex,
                # create DeviceInstance
                if ifIndex not in self.interfaces:
                    self.interfaces[ifIndex] = DeviceInterface(self, ifIndex)
                # Remove the part of the OID we used to walk on. Leave just the IP address part.
                # Add it to interface
                ip_address = '.'.join([
                    re.sub(oid_pattern, '', interface_address_result.oid),
                    interface_address_result.oid_index
                ])
                self.interfaces[ifIndex].add_ip_address(ip_address)

            return True
        except easysnmp.EasySNMPError:
            return False

    def check_ptrs(self):
        """
        Checks each IP address on the interface
        IP addresses that match A record are considered to be loopback addresses
        Those IPs have PTR pointing to device hostname rather than name in hostname-interface.domain.example format
        :return:
        """
        for interface in self.interfaces:
            for ip_address in self.interfaces[interface].ip_addresses:
                # If IP matches loopback IP, expected PTR is device.hostname
                if ip_address == self.ip:
                    existing_ptr, status = DnsCheck.get_status(ip_address, self.hostname)
                else:
                    existing_ptr, status = DnsCheck.get_status(ip_address, self.interfaces[interface].ptr)
                # Update PTR status in interfaces dictionary
                self.interfaces[interface].update_ptr_status(ip_address, existing_ptr, status)

    def __repr__(self):
        """
        Returns string representation of device status
        Also contains table with all interfaces, current (and new) PTRs, IP addresses
        :return:
        """
        # Top border
        str = '═' * 97 + "\n"
        # Ignored device message
        if self.ignored:
            str += "\n\033[93m\033[07m\033[04m DEVICE ON IGNORE LIST \033[0m\n\n"
        # Device information
        str += "\033[01mDevice:\t\t%s\n" % self.hostname
        str += "Interfaces:\t%d\n\033[0m" % len(self.interfaces)
        # Print interface table
        if len(self.interfaces):
            # Header
            str += '━' * 97 + "\n"
            str += "%-9s %-26s %-44s %s\n" % ('ifIndex', 'ifName', 'PTR', 'IP address')
            str += '─' * 97  + "\n"
            # Interface details
            for interface in self.interfaces:
                str += self.interfaces[interface].__repr__()
                str += "\033[90m" + '┈' * 97 + "\033[0m\n"
        # Bottom border
        str += '═' * 97  + "\n"
        return str