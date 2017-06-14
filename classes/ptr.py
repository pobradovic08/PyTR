# -*- coding: utf-8 -*-

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
