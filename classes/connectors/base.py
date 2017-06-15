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


class BaseConnector:
    """
    Interface for Connectors
    Connector class should be named as `ExampleConnector` where Example is connector name
    Connector name is used for fetching connector's configuration
    """

    def __init__(self, dispatcher):
        # Register connector with dispatcher
        dispatcher.register_connector(self)
        # Get connector's config
        self.config = dispatcher.get_connector_config(self)

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
