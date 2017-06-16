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
import logging
import MySQLdb


class ObserviumConnector(BaseConnector):
    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        self.logger = logging.getLogger('dns_update.connector.observium')
        mysql_data = self.config['mysql']
        self.logger.info("Connecting to '%s'@'%s' with username '%s'" % (
            mysql_data['db'],
            mysql_data['host'],
            mysql_data['user']
        ))
        self.db = MySQLdb.connect(**mysql_data)
        self.c = self.db.cursor()

    def load_devices(self):
        """
        Select all devices from observium database that are not disabled
        :return:
        """
        device_list = []
        sql = "SELECT hostname FROM devices WHERE disabled = 0"
        self.logger.debug("Executing SQL: %s" % sql)
        self.c.execute(sql)
        for hostname in self.c.fetchall():
            device_list.append(hostname[0])
        self.logger.debug("Fetched %s device(s) from database" % len(device_list))
        return device_list

    def save_ptr(self, ptr):
        """
        No need to update PTR in Observium
        :param ptr:
        :return:
        """
        pass

    def load_ptrs(self):
        """
        No PTR records in Observium
        :return:
        """
        pass
