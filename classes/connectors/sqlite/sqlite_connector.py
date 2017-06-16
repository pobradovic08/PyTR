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


import logging
import time
import sqlite3
from classes.connectors import BaseConnector
from classes import Ptr


class SqliteConnector(BaseConnector):
    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        self.logger = logging.getLogger('dns_update.connector.sqlite')
        self.logger.debug("Database file: '%s'" % self.config['db'])
        self.connection = sqlite3.connect(self.config['db'])
        self.logger.info("Database file '%s' loaded" % self.config['db'])
        self.c = self.connection.cursor()

    def create_ptr_table(self):
        sql = """CREATE TABLE IF NOT EXISTS `ptrs` (
                  `ip_address` INTEGER  NOT NULL PRIMARY KEY ,
                  `hostname` VARCHAR(128) DEFAULT NULL,
                  `if_name` VARCHAR(128) DEFAULT NULL,
                  `ptr` VARCHAR(128) DEFAULT NULL,
                  `ptr_zone` VARCHAR(128) NOT NULL,
                  `status` INTEGER UNSIGNED NOT NULL,
                  `insert_time` INTEGER UNSIGNED DEFAULT NULL,
                  `update_time` INTEGER UNSIGNED DEFAULT NULL
                )"""
        self.c.execute(sql)

    def drop_ptr_table(self):
        sql = "DROP TABLE IF EXISTS `ptrs`"
        self.c.execute(sql)

    def load_ptrs(self):
        ptrs = {}
        sql = "SELECT `ip_address`, `hostname`, `if_name`, `ptr`, `status` FROM `ptrs`"
        self.c.execute(sql)
        for ptr_row in self.c.fetchall():
            ptr = Ptr(
                ip_address=ptr_row[0],
                hostname=ptr_row[1],
                if_name=ptr_row[2],
                ptr=ptr_row[3],
                status=ptr_row[4]
            )
            ptrs[str(ptr.ip_address)] = ptr

        return ptrs

    def save_ptr(self, ptr):
        sql = "INSERT INTO `ptrs` VALUES (" \
              ":ip_address, :hostname, :if_name, :ptr, :ptr_zone, :status, :insert_time, :update_time" \
              ")"

        data = {
            "ip_address": ptr.ip_int(),
            "hostname": ptr.hostname,
            "if_name": ptr.if_name,
            "ptr": ptr.ptr,
            "ptr_zone": ptr.get_ptr_zone(),
            "status": ptr.status,
            "insert_time": int(time.time()),
            "update_time": int(time.time())
        }
        self.c.execute(sql, data)

    def load_devices(self):
        pass
