# -*- coding: utf-8 -*-

import re
from easysnmp import Session, EasySNMPNoSuchInstanceError
from dns_check import DnsCheck


class DeviceInterface:
    def __init__(self, device, ifIndex):
        self.device = device
        self.ip_addresses = {}
        self.ifIndex = ifIndex
        self.ptr = None
        self.short_ptr = None
        self.get_if_name()

    def get_if_name(self):
        # Append interface index to IF-MIB::ifName OID
        ifName_result = self.device.session.get('.1.3.6.1.2.1.31.1.1.1.1.' + str(self.ifIndex))
        self.ifName = ifName_result.value
        # Make PTR
        self._make_ptr()

    def _make_ptr(self):
        """
        Generate PTR from hostname, interface name and domain
        """
        # Convert to lowercase and replace all chars not letters, numbers and dash (-) with dash
        interface = self.ifName.lower()
        interface = re.sub(r'[^a-zA-Z0-9-]', '-', interface)
        # If interface name is longer than 10 characters (ios-xr etc.)
        # Take first two letters from interface prefix (interface type)
        # Replace all letters from suffix (interface number) leaving just integers and separators
        if len(interface) > 10:
            try:
                x = re.match(r"([^0-9]{2}).*?([0-9].*)", interface)
                interface = x.group(1) + re.sub(r'[a-zA-Z]', '', x.group(2))
            except AttributeError:
                #TODO: what if interface doesn't have group(2)?
                pass
        # Move format string to config file?
        self.ptr = '{host}-{interface}.{domain}'.format(
            host=self.device.host, interface=interface, domain=self.device.domain
        )
        self.short_ptr = '{host}-{interface}'.format(
            host=self.device.host, interface=interface
        )

    def add_ip_address(self, ip_address):
        """ Add ip address to address list in case interface has multiple addresses """
        if ip_address not in self.ip_addresses:
            self.ip_addresses[ip_address] = {
                'existing_ptr': None,
                'status': DnsCheck.STATUS_UNKNOWN
            }

    def update_ptr_status(self, ip_address, ptr, status):
        if ip_address in self.ip_addresses:
            self.ip_addresses[ip_address]['existing_ptr'] = ptr
            self.ip_addresses[ip_address]['status'] = status

    def get_ptr_for_ip(self, ip_address):
        if self.device.config.terse:
            return self.get_short_ptr(ip_address)
        else:
            return self.get_full_ptr(ip_address)

    def get_short_ptr(self, ip_address):
        return self.short_ptr if not ip_address == self.device.ip else self.device.host + " ★"

    def get_full_ptr(self, ip_address):
        return self.ptr if not ip_address == self.device.ip else self.device.hostname + " ★"


    def print_table_row(self):
        string = self.__repr__()
        if len(string):
            string += "├" + '─' * 95 + "┤\n"
        return string

    def print_ok_row(self, ip):
        if self.device.config.diff_only:
            return None
        color = "\033[92m"  # Green
        icon = '■'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            self.ifName,
            icon,
            self.get_ptr_for_ip(ip),
            ip
        )

    def print_not_updated_row(self, ip):
        color = "\033[93m"
        icon = '┌'
        output_string = "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            self.ifName,
            icon,
            self.ip_addresses[ip]['existing_ptr'],
            ip
        )
        output_string += "│%s%24s └─► %s%-66s\033[0;0m│\n" % (
            color,
            ' ', "\033[01m",  # Bold
            self.get_ptr_for_ip(ip)  # If IP is from A RR print hostname
        )

    def print_not_created_row(self, ip):
        color = "\033[01m\033[91m" # Bold red
        icon = '■'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            self.ifName,
            icon,
            self.get_ptr_for_ip(ip),
            ip
        )

    def print_unknown_row(self, ip):
        if self.device.config.diff_only:
            return None
        color = "\033[90m"  # Grey
        icon = 'i'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            self.ifName,
            icon,
            self.get_ptr_for_ip(ip),
            ip
        )

    def print_default_row(self, ip):
        if self.device.config.diff_only:
            return None
        color = "\033[90m"  # Grey
        icon = '☓'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            self.ifName,
            icon,
            self.get_ptr_for_ip(ip),
            ip
        )

    def __repr__(self):
        output_array = []
        for ip in self.ip_addresses:
            output_string = ''
            ip_status = self.ip_addresses[ip]['status']
            if ip_status == DnsCheck.STATUS_OK:
                output_array.append(self.print_ok_row(ip))
            elif ip_status == DnsCheck.STATUS_NOT_UPDATED:
                output_array.append(self.print_not_updated_row(ip))
            elif ip_status == DnsCheck.STATUS_NOT_CREATED:
                output_array.append(self.print_not_created_row(ip))
            elif ip_status == DnsCheck.STATUS_UNKNOWN:
                output_array.append(self.print_unknown_row(ip))
            else:
                output_array.append(self.print_default_row(ip))
        return ''.join(filter(None, output_array))
