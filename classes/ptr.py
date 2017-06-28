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


import ipaddress
import logging


class Ptr:
    STATUS_UNKNOWN = 0
    STATUS_OK = 1
    STATUS_NOT_UPDATED = 2
    STATUS_NOT_CREATED = 3
    STATUS_NOT_AUTHORITATIVE = 4
    STATUS_IGNORED = 5

    def __init__(self, ip_address, ptr, hostname, if_name, status=STATUS_UNKNOWN):
        # type: (unicode, str, str, str, str) -> None
        self.logger = logging.getLogger('dns_update.ptr')
        self.ip_address = None
        try:
            if isinstance(ip_address, (int, long)):
                self.ip_address = ipaddress.IPv4Address(ip_address)
            else:
                self.ip_address = ipaddress.IPv4Address(ip_address.decode('utf-8'))
        except ipaddress.AddressValueError as e:
            raise ValueError("Invalid IP address: %s" % e)
        self.hostname = hostname
        self.if_name = if_name
        self.ptr = ptr
        self.status = status

    # noinspection PyTypeChecker
    def ip_int(self):
        return int(self.ip_address)

    @classmethod
    def get_ip_int(cls, ip_address):
        """
        Get int (long) representation of the IP address
        :param ip_address:
        :return:
        """
        try:
            ip = ipaddress.IPv4Address(ip_address.decode('utf-8'))
            return int(ip)
        except ipaddress.AddressValueError as e:
            raise ValueError("Invalid IP address: %s" % e)

    def get_ptr_zone(self):
        """ Returns ptr zone in x.y.z.in-addr.arpa format """
        # Get first 3 octets, reverse them and append '.in-addr.arpa.'
        parts = str(self.ip_address).split('.')
        zone = '.'.join(list(reversed(parts[:-1]))) + '.in-addr.arpa.'
        return zone

    def __repr__(self):
        return "%s (%s)" % (self.ptr, self.ip_address)
