# -*- coding: utf-8 -*-


class BaseOutput:
    def __init__(self):
        pass

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
    def display_interface_detailed(device_interface):
        raise NotImplementedError

    @staticmethod
    def _lvmap(value, x_start, x_end, u_start, u_end):
        """
        Linear vector mapping
        :param value:  Value in [x_start, x_end] (converted to float)
        :param x_start: Start value of base range
        :param x_end:  End value of base range
        :param u_start: Start value of mapped range
        :param u_end: End value of mapped range
        :return:
        """
        return u_start + ((u_end - u_start) * ((float(value) - x_start) / (x_end - x_start)))