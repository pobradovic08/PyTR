# -*- coding: utf-8 -*-

import re
from dns_check import DnsCheck
from ptr import Ptr


class DeviceInterface:
    def __init__(self, device, if_index):
        self.device = device
        self.ip_addresses = {}
        self.if_index = if_index
        self.if_name = None
        self.ptr = None
        self.short_ptr = None
        self.get_if_name()

    def get_if_name(self):
        """
        Get ifName SNMP table and make PTRs
        :return:
        """
        # Append interface index to IF-MIB::ifName OID
        if_name_result = self.device.session.get('.1.3.6.1.2.1.31.1.1.1.1.' + str(self.if_index))
        self.if_name = if_name_result.value
        # Make PTR
        self._make_ptr()

    def _make_ptr(self):
        """
        Generate PTR from hostname, interface name and domain
        """
        # Convert to lowercase and replace all chars not letters, numbers and dash (-) with dash
        interface = self.if_name.lower()
        interface = re.sub(r'[^a-zA-Z0-9-]', '-', interface)
        # If interface name is longer than 10 characters (ios-xr etc.)
        # Take first two letters from interface prefix (interface type)
        # Replace all letters from suffix (interface number) leaving just integers and separators
        if len(interface) > 10:
            try:
                x = re.match(r"([^0-9]{2}).*?([0-9].*)", interface)
                interface = x.group(1) + re.sub(r'[a-zA-Z]', '', x.group(2))
                interface = interface.strip('-')    # Mikrotik stuff
            except AttributeError:
                # TODO: what if interface doesn't have group(2)?
                pass
        # Move format string to config file?
        self.ptr = '{host}-{interface}.{domain}'.format(
            host=self.device.host, interface=interface, domain=self.device.domain
        )
        self.short_ptr = '{host}-{interface}'.format(
            host=self.device.host, interface=interface
        )

    def add_ip_address(self, ip_address):
        """
        Add ip address to address list in case interface has multiple addresses
        :param ip_address:  IP address
        :return:
        """
        if ip_address not in self.ip_addresses:
            self.ip_addresses[ip_address] = {
                'existing_ptr': None,
                'status': DnsCheck.STATUS_UNKNOWN
            }

    def update_ptr_status(self, ip_address, ptr, status):
        """
        Update PTR status
        :param ip_address:  IP address
        :param ptr: PTR record
        :param status: PTR status
        :return:
        """
        if ip_address in self.ip_addresses:
            self.ip_addresses[ip_address]['existing_ptr'] = ptr
            self.ip_addresses[ip_address]['status'] = status

    def get_ptr_for_ip(self, ip_address):
        """
        Depending on selected output mode return short or FQDN PTRs
        :param ip_address: IP address
        :return:
        """
        if self.device.config.terse:
            return self._get_short_ptr(ip_address)
        else:
            return self._get_full_ptr(ip_address)

    def _get_short_ptr(self, ip_address):
        """
        Returns short (no domain) PTR for given IP address
        :param ip_address:  IP address
        :return:
        """
        return self.short_ptr if not ip_address == self.device.ip else self.device.host

    def _get_full_ptr(self, ip_address):
        """
        Returns full (FQDN) PTR for given IP address
        :param ip_address:
        :return:
        """
        return self.ptr if not ip_address == self.device.ip else self.device.hostname

    def get_ptrs(self):
        """
        Return ptr records for this interface.
        Each IP address has it's own PTR record.
        Loopback IP has a hostname as PTR
        :return:
        """
        ptrs = {}
        for ip in self.ip_addresses:
            try:
                ptrs[ip] = Ptr(
                    ip=ip,
                    device=self.device.hostname,
                    interface=self.if_name,
                    ptr=self._get_full_ptr(ip),
                    status=self.ip_addresses[ip]['status']
                )
            except ValueError:
                # TODO: Logging
                continue
        return ptrs
