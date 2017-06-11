#-*- coding: utf-8 -*-

class Base:

    @staticmethod
    def display_summary(dispatcher):
        raise NotImplementedError

    @staticmethod
    def display_detailed(dispatcher):
        raise NotImplementedError

    @staticmethod
    def display_device_summary(device):
        raise NotImplementedError

    @staticmethod
    def display_device_detailed(device):
        raise NotImplementedError

    @staticmethod
    def display_interface_summary(device_interface):
        raise NotImplementedError

    @staticmethod
    def display_interface_detailed(device_interface):
        raise NotImplementedError