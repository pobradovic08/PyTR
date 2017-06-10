#-*- coding: utf-8 -*-

class BaseInterface():

    def load_devices(self):
        """
        Should return list of FQDNs of devices you want to check
        :return:
        """
        raise NotImplementedError()

    def save_ptr(self, ptr):
        raise NotImplementedError()

