# -*- coding: utf-8 -*-
import re, sre_constants

import easysnmp
from device_interface import DeviceInterface
from dns_check import DnsCheck
from config import Config


class Device:

    def __init__(self, hostname, config, dns = None):
        """
        Initialize instance with empty interfaces array
        :param hostname:    Hostname of device. If it's not FQDN we will try to resolve to one
        :param config:      Config instance
        """

        self.config = config
        self.interfaces = {}
        self.ignored = False

        self.dns = dns if dns else DnsCheck(self.config)

        # Try to get FQDN for the hostname
        # If it fails, use provided hostname
        self.hostname = DnsCheck.get_fqdn(hostname)
        if not self.hostname:
            self.hostname = hostname

        # Split device.hostname into two parts: (hostname).(domain.example)
        self.host, self.domain = self.hostname.split('.', 1)

        # Get IN A record for device hostname
        self.ip = DnsCheck.get_a(self.hostname)

        # TODO: update to support v3
        self.community = config.get_snmp_community(self.hostname)

        # Configuration
        configuration = Config()

        self.ignored = configuration.is_device_ignored(self.hostname)

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

        # Setup SNMP session
        try:
            self.session = easysnmp.Session(
                hostname=self.hostname,
                community=self.community,
                use_numeric=True,
                version=2,
                timeout=self.config.get_snmp_timeout(),
                retries=self.config.get_snmp_retries(),
                abort_on_nonexistent=True
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
                    # Some devices will have loopback IP and ifIndex
                    # But no ifName associated with that ifIndex
                    # We can skip those since we can't make PTRs
                    try:
                        self.interfaces[ifIndex] = DeviceInterface(self, ifIndex)
                    except easysnmp.EasySNMPNoSuchInstanceError:
                        continue
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
                if self.config.is_interface_ignored(self.hostname, self.interfaces[interface].ifName):
                    self.interfaces[interface].update_ptr_status(ip_address, None, DnsCheck.STATUS_UNKNOWN)
                    continue
                # If IP matches loopback IP, expected PTR is device.hostname
                if ip_address == self.ip:
                    existing_ptr, status = self.dns.get_status(ip_address, self.hostname)
                else:
                    existing_ptr, status = self.dns.get_status(ip_address, self.interfaces[interface].ptr)
                # Update PTR status in interfaces dictionary
                self.interfaces[interface].update_ptr_status(ip_address, existing_ptr, status)

    def get_number_of_interfaces(self):
        """
        Return total number of interfaces on device
        :return:
        """
        return len(self.interfaces)

    def get_number_of_ip_addresses(self):
        """
        Return total number of IP addresses on device
        :return:
        """
        num = 0
        for interface in self.interfaces:
            num += len(self.interfaces[interface].ip_addresses)

        return num

    def __repr__(self):
        """
        Returns string representation of device status
        Also contains table with all interfaces, current (and new) PTRs, IP addresses
        :return:
        """
        # Table info header
        # Top border
        output_string = '═' * 97 + "\n"
        # Ignored device message
        if self.ignored:
            output_string += "\n\033[93m\033[07m\033[04m DEVICE ON IGNORE LIST \033[0m\n\n"
        # Device information
        output_string += "\033[01m" # Formatting - bold
        output_string += "Device:\t\t%s\n" % self.hostname
        output_string += "Interfaces:\t%d\n" % self.get_number_of_interfaces()
        output_string += "IP addresses:\t%d\n" % self.get_number_of_ip_addresses()
        output_string += "\033[0m" # Formatting - reset

        # Print interface table
        if len(self.interfaces):
            # Table interface header
            output_string += '━' * 97 + "\n"
            output_string += "%-9s %-26s %-44s %s\n" % ('ifIndex', 'ifName', 'PTR', 'IP address')
            output_string += '─' * 97  + "\n"
            # Interface details
            # DeviceInterface output list
            interface_rows = []
            for interface in self.interfaces:
                # DeviceInterface output
                interface_row = self.interfaces[interface].print_table_row()
                # Interface row could be empty if interface status is OK and diff switch is used
                # Avoid adding empty strings to interface_rows list
                if interface_row:
                    interface_rows.append(interface_row)
            # Print info instead of empty table
            if not len(interface_rows):
                output_string += "No PTRs to update\n"
            else:
                output_string += ''.join(interface_rows)

        # Bottom border
        output_string += '═' * 97  + "\n"
        return output_string

