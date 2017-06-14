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

    def __init__(self, ip, ptr, device, interface, status=STATUS_UNKNOWN):
        self.logger = logging.getLogger('dns_update.ptr')
        try:
            self.ip = ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError as e:
            raise ValueError("Invalid IP address: %s" % e)
        self.device = device
        self.interface = interface
        self.ptr = ptr
        self.status = status

    def __repr__(self):
        return "%s (%s)" % (self.ptr, self.ip)
