#-*- coding: utf-8 -*-

class BaseInterface():

    def __init__(self, dispatcher):
        dispatcher.register_connector(self)

    def load_devices(self):
        """
        Should return list of FQDNs of devices you want to check
        :return:
        """
        raise NotImplementedError()

    def save_ptr(self, ptr):
        """
        Saves passed PTR record to destination. PTR record is in format:
        {
            device: FQDN,
            interface: IF-MIB::ifIndex,
            ptr: interface-host.domain.example,
            ip: IP address
        }
        :param ptr: PTR dictionary containing: device, interface, ptr, ip_address
        :return:
        """
        raise NotImplementedError()

