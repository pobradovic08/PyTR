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


import re
import logging
from dns_check import DnsCheck
from ptr import Ptr


class DeviceInterface:
    def __init__(self, device, if_index):
        self.logger = logging.getLogger('dns_update.device_interface:%s:ifIndex.%d' % (device.hostname, if_index))
        self.logger.debug("Created DeviceInterface object")
        self.device = device
        self.ip_addresses = {}
        self.if_index = if_index
        self.if_name = None
        self.ptr = None
        self.short_ptr = None
        self.get_if_name()
        self.ignored = self.device.config.is_interface_ignored(self.device.hostname,self.if_name)

    def get_if_name(self):
        """
        Get ifName SNMP table and make PTRs
        :return:
        """
        # Append interface index to IF-MIB::ifName OID
        if_name_result = self.device.session.get('.1.3.6.1.2.1.31.1.1.1.1.' + str(self.if_index))
        self.if_name = if_name_result.value
        self.logger.debug("Set ifName to %s" % self.if_name)
        # Make PTR
        self._make_ptr()

    def _make_ptr(self):
        """
        Generate PTR from hostname, interface name and domain
        """
        # Convert to lowercase and replace all chars not letters, numbers and dash (-) with dash
        interface = self.if_name.lower()
        interface = re.sub(r'[^a-zA-Z0-9-]', '-', interface)
        self.logger.debug("Interface part of the PTR set to '%s'" % interface)
        # If interface name is longer than 10 characters (ios-xr etc.)
        # Take first two letters from interface prefix (interface type)
        # Replace all letters from suffix (interface number) leaving just integers and separators
        if len(interface) > 10:
            try:
                x = re.match(r"([^0-9]{2}).*?([0-9].*)", interface)
                interface = x.group(1) + re.sub(r'[a-zA-Z]', '', x.group(2))
                interface = interface.strip('-')  # Mikrotik stuff
                self.logger.debug("Interface part of the PTR shortened to '%s'" % interface)
            except AttributeError:
                # TODO: what if interface has 10+ chars but have group(2) (number suffix)? Fix above pls
                self.logger.warning("Unable to parse and shorten '%s' interface name" % interface)
        # Move format string to config file?
        self.short_ptr = '{host}-{interface}'.format(
            host=self.device.host, interface=interface
        )
        self.ptr = '.'.join(filter(None, [self.short_ptr, self.device.domain]))
        self.logger.info("PTR for interface '%s' set to: '%s'" % (self.if_name, self.ptr))

    def check_ptr(self):
        self.logger.debug(
            "Interface '%s' has %d IP address(es)" % (
                self.if_name,
                len(self.ip_addresses)
            )
        )
        if self.ignored:
            return
        for ip_address in self.ip_addresses:
            # Check if interface or IP is ignored
            if self.device.config.is_ip_ignored(ip_address):
                self.update_ptr_status(ip_address, None, DnsCheck.STATUS_IGNORED)
                self.logger.info("Interface '%s' or IP address '%s' are on ignore list" % (
                    self.if_name,
                    ip_address
                ))
                return

            # If IP matches loopback IP, expected PTR is device.hostname
            if ip_address == self.device.ip:
                existing_ptr, status = self.device.dns.get_status(ip_address, self.device.hostname)
            else:
                existing_ptr, status = self.device.dns.get_status(ip_address, self.ptr)

            # Update PTR status in interfaces dictionary
            self.logger.debug("Update DeviceInterface PTR status for '%s' to '%d'" % (ip_address, status))
            self.update_ptr_status(ip_address, existing_ptr, status)

    def add_ip_address(self, ip_address):
        """
        Add ip address to address list in case interface has multiple addresses
        :param ip_address:  IP address
        :return:
        """
        self.logger.debug("Called with '%s'" % ip_address)
        if ip_address not in self.ip_addresses:
            self.ip_addresses[ip_address] = {
                'existing_ptr': None,
                'status': DnsCheck.STATUS_UNKNOWN
            }
            self.logger.debug("Address added with default status (UNKNOWN)")
            return True
        else:
            self.logger.warning("Address %s already exists on interface, skipping" % ip_address)
            return False

    def update_ptr_status(self, ip_address, ptr, status):
        """
        Update PTR status
        :param ip_address:  IP address
        :param ptr: PTR record
        :param status: PTR status
        :return:
        """
        self.logger.debug("Called for IP: %s" % ip_address)
        if ip_address in self.ip_addresses:
            self.ip_addresses[ip_address]['existing_ptr'] = ptr
            self.ip_addresses[ip_address]['status'] = status
            self.logger.debug("PTR '%s' added with status (%d)" % (ptr, status))
            return True
        else:
            self.logger.warning("Address %s doesn't exists, skipping" % ip_address)
            return False

    def get_ptr_for_ip(self, ip_address):
        """
        Depending on selected output mode return short or FQDN PTRs
        :param ip_address: IP address
        :return:
        """
        self.logger.debug("Called for IP: %s" % ip_address)
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
        self.logger.debug("Total number of IPs: %d" % (len(self.ip_addresses)))
        ptrs = {}
        for ip in self.ip_addresses:
            try:
                ptrs[ip] = Ptr(
                    ip_address=ip,
                    hostname=self.device.hostname,
                    if_name=self.if_name,
                    ptr=self._get_full_ptr(ip),
                    status=self.ip_addresses[ip]['status']
                )
                self.logger.debug("Prepared PTR: %s" % ptrs[ip])
            except ValueError as e:
                self.logger.warning("Can't create PTR: %s" % e)
                continue
        self.logger.info("Returned %d PTRs for interface '%s'" % (len(ptrs), self.if_name))
        return ptrs
