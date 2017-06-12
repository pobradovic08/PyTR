#-*- coding: utf-8 -*-

import ipaddress

class Ptr:

    def __init__(self, ip, ptr, device, interface):
        try:
            self.ip = ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError as e:
            raise ValueError("Invalid IP address: %s" % e)
        self.device = device
        self.interface = interface
        self.ptr = ptr