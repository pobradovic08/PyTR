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
        if 'retries' in self.data['snmp']:
            try:
                return int(self.data['snmp']['retries'])
            except ValueError:
                print "Configuration file invalid (snmp->retries)"
                return default
        else:
            return default
