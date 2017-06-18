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


import os
import imp
import logging
from classes import DnsCheck
from classes import Device


class Dispatcher:
    """

    Registers connectors (interfaces) to various input and output methods
    Maintains the dict of devices and ptrs

    """

    def __init__(self, config, auto_load=True, connectors_dir='/connectors'):
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
            path = os.path.dirname(os.path.abspath(__file__)) + connectors_dir
            self.logger.info("Autoload enabled. Searching: '%s'" % path)
            for dirname in [d for d in os.listdir(path) if os.path.isdir(path + '/' + d)]:
                filename = dirname + '_connector.py'
                py = filename[:-3]
                class_name = ''.join([x.capitalize() for x in py.split('_')])
                try:
                    mod = imp.load_source(class_name, path + '/' + dirname + '/' + filename)
                    # Instantiate class
                    if hasattr(mod, class_name):
                        getattr(mod, class_name)(self)
                        self.logger.info("Connector '%s' successfully loaded" % class_name)
                    else:
                        self.logger.error("Connector '%s' couldn't be loaded" % class_name)
                except IOError:
                    self.logger.error("Connector's '%s' directory doesn't have '%s' file" % (class_name, filename))
                    continue

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
        connector_name = connector.get_connector_name()
        self.logger.debug("Search for ['%s'] in configuration file" % connector_name)
        return self.config.get_connector_config(connector_name)

    def save_ptr(self, ptr):
        """
        Issue save command on each connector
        :param ptr: PTR dict
        :return:
        """
        self.logger.info("Dispatch save PTR command for %s to all (%d) connectors" % (ptr, len(self.__connectors)))
        for connector in self.__connectors:
            connector.save_ptr(ptr)

    def save_ptrs(self, ptrs):
        """
        Issue save multiple PTRs command on each connector
        :param ptrs: PTR dict
        :return:
        """
        self.logger.info("Dispatch save PTRs command for %d PTRs to all (%d) connectors" % (
            len(ptrs), len(self.__connectors)
        ))
        for connector in self.__connectors:
            connector.save_ptrs(ptrs)

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
            device_list += filter(lambda x: len(x) > 0, connector.load_devices())

        # Populate devices dict from temporary list
        for device in device_list:
            hostname = self.dns.get_fqdn(device)
            if hostname:
                if hostname not in self.devices:
                    self.devices[hostname] = Device(hostname, self.config, self.dns)
            else:
                self.logger.warning("Hostname '%s' couldn't be resolved. SKipping..." % device)
                pass

        self.logger.info("Loaded %d device(s) from %d connectors" % (len(device_list), len(self.__connectors)))
