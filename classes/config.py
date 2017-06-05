#-*- coding: utf-8 -*-
import json
import re, sre_constants

class Config:

    def __init__(self, filename = 'configuration.json'):
        """
        Provides interface to JSON configuration file.
        :param filename: Default file is configuration.json in script root directory
        """
        with open(filename) as data_file:
            self.data = json.load(data_file)

    def get_ns_servers(self):
        """
        Returns 'dns'->'servers' dictionary
        :return:
        """
        return self.data['dns']['servers']

    def get_ignore_rules(self):
        """
        Returns 'ignore' dictionary
        :return:
        """
        try:
            return self.data['ignore']
        except KeyError:
            return {}

    def get_snmp_community(self, hostname=None):
        """
        Returns SNMP community for given hostname
        :return:
        """
        default = self.data['snmp']['community']['default']
        if not hostname:
            return default
        try:
            overridden = self.data['snmp']['community']['override']
            for hostname_match, community in overridden.iteritems():
                try:
                    if re.match(hostname_match, hostname):
                        return community
                except sre_constants.error:
                    print "Custom SNMP community rule in Config not valid"
                    continue
        except KeyError:
            pass
        return default

    def get_snmp_retries(self, default = 0):
        """
        Returns number of retries for SNMP queries
        :param default: Default value returned if there's no value in Config. Must be int >= 0
        :return:
        """

        # Try integer conversion (raises ValueError on failure)
        default = int(default)
        # Raise ValueError if value is not positive (or 0)
        if default < 0:
            raise ValueError("SNMP retries value must be 0 or positive integer")

        # Fetches snmp->retries from config file if it exists
        if 'retries' in self.data['snmp']:
            try:
                # If value in configuration file is wrong return default value in except
                config_value = int(self.data['snmp']['retries'])
                if config_value < 0:
                    raise ValueError("Invalid config file. SNMP retries must be 0 or positive integer")
                return config_value

            except ValueError:
                print "Configuration file invalid (snmp->retries)"
                return default
        else:
            return default


    def get_snmp_timeout(self, default = 1):
        """
        Returns value for timeout
        :param default: Default value returned if there's no value in Config. Must be positive value
        :return:
        """
        default = float(default)
        if default <= 0:
            raise ValueError("Timeout must be positive")

        if 'timeout' in self.data['snmp']:
            try:
                config_value = float(self.data['snmp']['timeout'])
                if config_value <= 0:
                    raise ValueError("Invalid config file. SNMP timeout must be positive")
                return config_value

            except ValueError:
                print "Configuration file invalid (snmp->retries)"
                return default
        else:
            return default


    def is_device_ignored(self, hostname):
        """
        Go trough each ignore rule and check
        if the Config hostname regexp matches provided hostname
        :param hostname:  Device hostname
        :return:
        """
        for rule_name, rule in self.get_ignore_rules().iteritems():
            try:
                if re.match(rule['hostname'], hostname):
                    return True
            except sre_constants.error:
                #TODO: Real logging, not this shit
                print "Rule '%s' in configuration file invalid, skipping..." % rule_name
        return False