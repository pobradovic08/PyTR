#-*- coding: utf-8 -*-

class Ptr:

    def __init__(self, ip, ptr, device, interface):
        self.ip = ip
        self.device = device
        self.interface = interface
        self.ptr = ptr