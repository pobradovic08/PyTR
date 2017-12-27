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

from classes.connectors.base import BaseConnector
from classes import Ptr
import dns.query
import dns.tsigkeyring
import dns.update
import ipaddress
from dns.tsig import HMAC_MD5
import logging

__version__ = '0.4.4'


class DnsConnector(BaseConnector):
    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        self.logger = logging.getLogger('dns_update.connector.dns')
        self.dns_hostname = self.config['hostname']
        self.keyring = dns.tsigkeyring.from_text({
            'nsupdate_key': self.config['key']
        })

    def delete_ptr(self, ip_address):
        name, zone = str(dns.reversename.from_address(ip_address)).split('.', 1)
        update = dns.update.Update(zone, keyring=self.keyring, keyalgorithm=HMAC_MD5)
        update.delete(name)
        dns.query.tcp(update, self.dns_hostname)

    def create_ptr(self, ptr):
        if not isinstance(ptr, Ptr):
            raise ValueError("Argument must be of Ptr class.")
        update = dns.update.Update(ptr.get_ptr_zone(), keyring=self.keyring, keyalgorithm=HMAC_MD5)
        update.replace(ptr.get_ptr_zone_name(), 300, 'PTR', ptr.ptr)
        self.logger.debug("Updating %s" % self.dns_hostname)
        dns.query.tcp(update, self.dns_hostname)

    def delete_stale_ptrs(self):
        pass

    def delete_ptrs(self, ip_addresses):
        for ip_address in ip_addresses:
            try:
                ipaddress.IPv4Address(ip_address.decode('utf-8'))
                self.delete_ptr(ip_address)
            except ipaddress.AddressValueError:
                continue

    def load_devices(self):
        return []

    def load_ptrs(self):
        return {}

    def save_ptrs(self, ptrs):
        self.logger.info("Saving %d PTRs to database..." % len(ptrs))
        for ptr in ptrs:
            self.create_ptr(ptrs[ptr])
        self.logger.info("Saved %d PTRs to database." % len(ptrs))
