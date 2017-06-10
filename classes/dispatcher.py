#-*- coding: utf-8 -*-

class Dispatcher:
    """
    Main class of the program

    Registers connectors (interfaces) to various input and output methods
    Maintains the dict of devices and ptrs

    """

    def __init__(self):
        # List of registered connectors
        self.__connectors = []

        # List of modified PTRs
        self.unsaved_ptrs = []

        # Dict of devices. Keyed by hostname (FQDN)
        self.devices = {}

    def register_connector(self, connector):
        """
        Register connector.
        This is called from Connector's __init__ method
        :param connector: Connector object
        :return:
        """
        self.__connectors.append(connector)

    def save_ptr(self, ptr):
        """
        Issue save command on each connector
        :param ptr: PTR dict
        :return:
        """
        for connector in self.__connectors:
            connector.save_ptr(ptr)

    def load(self):
        """
        Load list of devices from each connector
        Since devices dict is keyed by hostnames, there are no duplicates
        :return:
        """
        # Temporary list
        device_list = []
        # Concatenate device list from each connector to temporary list
        for connector in self.__connectors:
            device_list += connector.load_devices()

        # Populate devices dict from temporary list
        for device in device_list:
            if device not in self.devices:
                self.devices[device] = {}