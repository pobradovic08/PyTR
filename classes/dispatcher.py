# -*- coding: utf-8 -*-

import re
import os
import imp
import logging
from classes.dns_check import DnsCheck


class Dispatcher:
    """

    Registers connectors (interfaces) to various input and output methods
    Maintains the dict of devices and ptrs

    """

    def __init__(self, config, auto_load=True):
        self.logger = logging.getLogger('dns_update.dispatcher')
        # List of registered connectors
        self.__connectors = []
        # List of modified PTRs
        self.unsaved_ptrs = []
        # Dict of devices. Keyed by hostname (FQDN)
        self.devices = {}
        # Config
        self.config = config
        # DNS
        self.dns = DnsCheck(self.config)

        if auto_load:
            # Autoload all connectors
            ignored_files = ['base.py', '__init__.py']
            path = os.path.dirname(os.path.abspath(__file__)) + '/interfaces'
            self.logger.info("Autoload enabled. Searching: '%s'" % path)
            for filename in [f for f in os.listdir(path) if f.endswith('.py') and f not in ignored_files]:
                py = filename[:-3]
                class_name = ''.join([x.capitalize() for x in py.split('_')])
                mod = imp.load_source(class_name, path + '/' + filename)
                # Instantiate class
                if hasattr(mod, class_name):
                    getattr(mod, class_name)(self)
                    self.logger.info("Connector '%s' successfully loaded" % class_name)
                else:
                    self.logger.error("Connector '%s' couldn't be loaded" % class_name)

    def register_connector(self, connector):
        """
        Register connector.
        This is called from Connector's __init__ method
        :param connector: Connector object
        :return:
        """
        self.logger.debug("Register connector '%s; to dispatcher" % connector.__class__.__name__)
        self.__connectors.append(connector)

    def get_connector_list(self):
        return [x.__class__.__name__ for x in self.__connectors]

    def get_connector_config(self, connector):
        class_name = connector.__class__.__name__
        connector_name = re.match('(.*)Connector', class_name)
        self.logger.debug("Search for ['%s'] in configuration file" % connector_name)
        if connector_name.group(1):
            self.logger.debug("Configuration for '%s' found" % class_name)
            return self.config.get_connector_config(connector_name.group(1).lower())
        else:
            self.logger.warning("Configuration for '%s' not found" % class_name)

    def save_ptr(self, ptr):
        """
        Issue save command on each connector
        :param ptr: PTR dict
        :return:
        """
        self.logger.info("Dispatch save PTR command for %s to all (%d) connectors" % (ptr, len(self.__connectors)))
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

        self.logger.info("Dispatch load command to all (%d) connectors" % len(self.__connectors))
        # Concatenate device list from each connector to temporary list
        for connector in self.__connectors:
            device_list += connector.load_devices()

        # Populate devices dict from temporary list
        for device in device_list:
            hostname = self.dns.get_fqdn(device)
            if hostname:
                if hostname not in self.devices:
                    self.devices[hostname] = None
            else:
                self.logger.warning("Hostname '%s' couldn't be resolved" % hostname)
                pass

        self.logger.info("Loaded %d device(s) from %d connectors" % (len(device_list), len(self.__connectors)))
