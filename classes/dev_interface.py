# -*- coding: utf-8 -*-

import re
from easysnmp import Session, EasySNMPNoSuchInstanceError
from dns_check import DnsCheck


class DevInterface:
    def __init__(self, device, ifIndex):
        self.device = device
        self.ip_addresses = {}
        self.ifIndex = ifIndex
        self.ptr = None
        self.get_if_name()

    def get_if_name(self):
        """ Establish SNMP session to {device} and get ifName for {ifIndex} """
        session = Session(
            hostname=self.device.hostname,
            community=self.device.community,
            version=2,
            timeout=1,
            retries=0,
            abort_on_nonexistent=True
        )
        try:
            ifName_result = session.get('.1.3.6.1.2.1.31.1.1.1.1.' + str(self.ifIndex))
            self.ifName = ifName_result.value
            self._make_ptr()
        except EasySNMPNoSuchInstanceError:
            self.ifName = None

    def _make_ptr(self):
        """ Generate PTR from hostname, interface name and domain """
        # Split device.hostname into two parts: (hostname).(domain.example)
        host, domain = self.device.hostname.split('.', 1)
        # Convert to lowercase and replace all chars not letters, numbers and dash (-) with dash
        interface = self.ifName.lower()
        interface = re.sub(r'[^a-zA-Z0-9-]', '-', interface)
        # If interface name is longer than 10 characters (ios-xr etc.)
        # Take first two letters from interface prefix (interface type)
        # Replace all letters from suffix (interface number) leaving just integers and separators
        if len(interface) > 10:
            x = re.match(r"([^0-9]{2}).*?([0-9].*)", interface)
            interface = x.group(1) + re.sub(r'[a-zA-Z]', '', x.group(2))
        # Move format string to config file?
        name = '{host}-{interface}.{domain}'.format(
            host=host, interface=interface, domain=domain
        )
        self.ptr = name

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
        return self.ptr if not ip_address == self.device.ip else self.device.hostname + " ★"

    def __repr__(self):
        str = ''
        for ip in self.ip_addresses:
            ip_status = self.ip_addresses[ip]['status']
            if ip_status == DnsCheck.STATUS_OK:
                str += "\033[92m"
                icon = '■'
            elif ip_status == DnsCheck.STATUS_NOT_UPDATED:
                str += "\033[93m"
                icon = '┌'
            elif ip_status == DnsCheck.STATUS_NOT_CREATED:
                str += "\033[01m\033[91m"
                icon = '■'
            # TODO: Add STATUS_UNKNOWN to differentiate between it and NOT_AUTHORITATIVE
            else:
                icon = '☓'
                str += "\033[90m"

            str += "%-9d %-24s %s %-44s %s\n" % (
                self.ifIndex,
                self.ifName,
                icon,
                self.get_ptr_for_ip(ip) if not ip_status == DnsCheck.STATUS_NOT_UPDATED else self.ip_addresses[ip][
                    'existing_ptr'],
                ip
            )
            if ip_status == DnsCheck.STATUS_NOT_UPDATED:
                str += "%34s └─► %s%s\n" % (
                    ' ', "\033[01m",  # Bold
                    self.get_ptr_for_ip(ip)  # If IP is from A RR print hostname
                )
            str += "\033[0;0m"
        return str
