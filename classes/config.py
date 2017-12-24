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


import json
import ipaddress
import re
import sre_constants
import logging
import os

__version__ = '0.1.2'

class Config:
    def __init__(
            self,
            filename='configuration.json',
            check_only=False,
            diff_only=False,
            terse=False
    ):
        """
        Provides interface to JSON configuration file.
        :param filename: Default file is configuration.json in script root directory
        """
        self.logger = logging.getLogger('dns_update.config')
        self.check_only = check_only
        self.diff_only = diff_only
        self.terse = terse

        filename = os.path.dirname(os.path.abspath(__file__)) + '/../' + filename
        with open(filename) as data_file:
            try:
                self.data = json.load(data_file)
                self.logger.info("Loaded '%s' configuration file" % filename)
            except ValueError:
                self.logger.critical("Couldn't parse '%s' configuration file. Exiting..." % filename)
                exit(1)
        required = {
            'snmp': {
                'community': {
                    'default': {}
                }
            },
            "dns": {
                "servers": {},
                "search": {
                    "domains": {},
                    "servers": {}
                }
            }
        }
        self._check_required_keys(required, self.data)

    def _check_required_keys(self, keys, dictionary):
        """
        Recursively go trough `keys` structure and check if it exists within `dictionary`
        :param keys:
        :param dictionary:
        :return:
        """
        for key in keys:
            # If the key is not in dictionary raise error
            if key not in dictionary:
                self.logger.critical("Config file missing required parameters. Exiting...")
                exit(1)
            # If dictionary[key] has substructure go trough it
            if dictionary[key]:
                self._check_required_keys(keys[key], dictionary[key])

    def get_connector_config(self, connector_name):
        """
        Returns config specific to connector class
        :param connector_name: connector name (derived from class name)
        :return:
        """
        self.logger.debug("Get config for connector '%s'" % connector_name)
        if connector_name in self.data['connector']:
            self.logger.info("Config for connector '%s' loaded" % connector_name)
            return self.data['connector'][connector_name]
        else:
            self.logger.warning("No config found for connector '%s'" % connector_name)
            return {}

    def get_email_server(self):
        """
        Returns SMTP server for sending reports
        :return:
        """
        return self.data['email']['server']

    def get_email_from(self):
        """
        Returns 'From' email address for sending reports
        :return:
        """
        return self.data['email']['from']

    def get_email_to(self):
        """
        Returns list of 'To' email addresses for sending reports
        :return:
        """
        return self.data['email']['to']

    def get_ns_servers(self):
        """
        Returns list of DNS servers we can update
        :return:
        """
        return self.data['dns']['servers']

    def get_ns_search_domains(self):
        """
        Returns a list of domain names (search list)
        :return:
        """
        return self.data['dns']['search']['domains']

    def get_ns_query_servers(self):
        """
        Returns a list of DNS servers to query for records
        :return:
        """
        return self.data['dns']['search']['servers']

    def get_device_ignore_rules(self):
        """
        Returns ignore devices
        :return:
        """
        try:
            return self.data['ignored']['device']
        except KeyError:
            self.logger.warning("No ignored devices object rule")
            return {}

    def get_ip_ignore_rules(self):
        """
        Returns ignore ip
        :return:
        """
        try:
            return self.data['ignored']['ip']
        except KeyError:
            self.logger.warning("No ignored IPs object rule")
            return []

    def _get_snmp_overridden_communities(self):
        try:
            return self.data['snmp']['community']['override']
        except KeyError:
            self.logger.warning("No custom community object in configuration file")
            return {}

    def get_snmp_community(self, hostname=None):
        """
        Returns SNMP community for given hostname
        :return:
        """
        default = self.data['snmp']['community']['default']
        if not hostname:
            self.logger.info("No device specified, returning default community '%s'" % default)
            return default

        for hostname_match, community in self._get_snmp_overridden_communities().iteritems():
            try:
                if re.match(hostname_match, hostname):
                    self.logger.info("Community for '%s' found: '%s'" % (hostname, community))
                    return community
                else:
                    self.logger.debug("Community for '%s' not found in rule '%s'" % (hostname, hostname_match))
            except sre_constants.error:
                self.logger.error("Custom SNMP community rule '%s' not valid." % hostname_match)
                continue

        self.logger.info("No custom rules found for hostname, returning default community '%s'" % default)
        return default

    def get_snmp_retries(self, default=0):
        """
        Returns number of retries for SNMP queries
        :param default: No value in Config - default value returned . Must be int >= 0
        :return:
        """
        default = int(default)
        # Fetches snmp->retries from config file if it exists
        if 'retries' in self.data['snmp']:
            try:
                # If value in configuration file is wrong return default value in except
                config_value = int(self.data['snmp']['retries'])
                if config_value < 0:
                    self.logger.warning(
                        "Retry count in configuration file not positive integer. Returning default value of: %d"
                        % default
                    )
                    return default
                else:
                    self.logger.info("Retry count value in configuration file is: %d" % config_value)
                    return config_value

            except ValueError:
                self.logger.warning("Retry count not integer. Returning default value of: %d" % default)
                return default
        else:
            self.logger.warning("No value set in configuration. Returning default value of: %d" % default)
            return default

    def get_snmp_timeout(self, default=1):
        """
        Returns value for timeout
        :param default: No value in Config - Default value returned. Must be positive value
        :return:
        """
        default = float(default)
        if 'timeout' in self.data['snmp']:
            try:
                config_value = float(self.data['snmp']['timeout'])
                if config_value <= 0:
                    self.logger.warning(
                        "Timeout value in configuration not positive. Return default value of %d" % default
                    )
                    return default
                self.logger.info("Timeout value in configuration file is: %f" % config_value)
                return config_value

            except ValueError:
                self.logger.warning(
                    "Timeout value in configuration is invalid. Return default value of %d" % default
                )
                return default
        else:
            self.logger.warning("No value set in configuration. Returning default value of: %d" % default)
            return default

    def is_device_ignored(self, hostname):
        """
        Go trough each ignore rule and check
        if the Config hostname regexp matches provided hostname
        :param hostname:  Device hostname
        :return:
        """
        self.logger.debug("Checking if '%s' is on ignore list" % hostname)
        for hostname_rule, interface_rules in self.get_device_ignore_rules().iteritems():
            try:
                if re.match('^' + hostname_rule + '$', hostname) and not len(interface_rules):
                    self.logger.info("Device '%s' on ignore list." % hostname)
                    return True
            except sre_constants.error:
                self.logger.error("Rule '%s' in configuration file invalid, skipping..." % hostname_rule)
        self.logger.debug("Device '%s' NOT on ignore list." % hostname)
        return False

    def is_interface_ignored(self, hostname, if_name):
        """
        Go trough each ignore rule and check
        if the Config hostname regexp matches provided hostname
        AND interface regexp matches provided ifName
        :param hostname:    Device hostname
        :param if_name:      Interface name
        :return:
        """
        self.logger.debug("Checking if interface '%s' on '%s' is on ignore list" % (if_name, hostname))
        for hostname_rule, interface_rules in self.get_device_ignore_rules().iteritems():
            try:
                if re.match('^' + hostname_rule + '$', hostname):
                    if not len(interface_rules):
                        self.logger.info("All interfaces for device '%s' are ignored" % hostname)
                        return True
                    for interface_rule in interface_rules:
                        if re.match('^' + interface_rule + '$', if_name):
                            self.logger.info("Interface '%s' on '%s' on ignore list." % (if_name, hostname))
                            return True
            except sre_constants.error as e:
                self.logger.error("Rule in configuration file invalid: %s" % e)
        self.logger.debug("Interface '%s' on '%s' NOT on ignore list." % (if_name, hostname))
        return False

    def is_ip_ignored(self, ip_address):
        self.logger.debug("Checking if IP '%s' is on ignore list" % ip_address)
        for ip_rule in self.get_ip_ignore_rules():
            try:
                network = ipaddress.IPv4Network(ip_rule)
                if ipaddress.IPv4Address(ip_address.decode('utf-8')) in network:
                    self.logger.info("IP '%s' is on ignore list." % ip_address)
                    return True
            except ipaddress.AddressValueError:
                self.logger.error("Invalid address in '%s' configuration rule" % ip_rule)
                continue
            except ipaddress.NetmaskValueError:
                self.logger.error("Invalid mask in '%s' configuration rule" % ip_rule)
                continue
        self.logger.debug("IP '%s' NOT on ignore list." % ip_address)
        return False
