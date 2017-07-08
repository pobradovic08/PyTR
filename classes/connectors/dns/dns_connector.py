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
import dns.query
import dns.tsigkeyring
import dns.update
from dns.tsig import HMAC_SHA256
import logging


class DnsConnector(BaseConnector):
    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        self.logger = logging.getLogger('dns_update.connector.dns')
        self.keyring = dns.tsigkeyring.from_text({
            'nsupdate_key': self.config['key']
        })

    def delete_stale_ptrs(self):
        pass

    def delete_ptrs(self, ip_addresses):
        pass

    def load_devices(self):
        return []

    def load_ptrs(self):
        return {}

    def save_ptrs(self, ptrs):
        pass
