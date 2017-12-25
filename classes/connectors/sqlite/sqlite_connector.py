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
import calendar
import sqlite3
from classes.connectors import BaseConnector
from classes import Ptr

__version__ = '0.2.0'


# noinspection SqlResolve
class SqliteConnector(BaseConnector):
    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        self.logger = logging.getLogger('dns_update.connector.sqlite')
        self.logger.debug("Database file: '%s'" % self.config['db'])
        self.connection = sqlite3.connect(self.config['db'])
        self.logger.info("Database file '%s' loaded" % self.config['db'])
        self.c = self.connection.cursor()
        try:
            self.c.execute("SELECT COUNT(*) FROM `ptrs`")
            self.logger.info("%s existing PTRs in database." % self.c.fetchall()[0][0])
        except sqlite3.OperationalError:
            self.logger.warning("Table `ptrs` doesn't exists. Creating...")
            self.create_ptr_table()

    def create_ptr_table(self):
        """
        Create PTR table
        :return:
        """
        sql = """CREATE TABLE IF NOT EXISTS `ptrs` (
                  `ip_address` INTEGER  NOT NULL PRIMARY KEY ,
                  `hostname` VARCHAR(128) DEFAULT NULL,
                  `if_name` VARCHAR(128) DEFAULT NULL,
                  `ptr` VARCHAR(128) DEFAULT NULL,
                  `ptr_zone` VARCHAR(128) NOT NULL,
                  `status` INTEGER UNSIGNED NOT NULL,
                  `insert_time` INTEGER UNSIGNED DEFAULT NULL
                )"""
        self.c.execute(sql)

    def drop_ptr_table(self):
        """
        Drop PTR table
        :return:
        """
        sql = "DROP TABLE IF EXISTS `ptrs`"
        self.c.execute(sql)

    def ptr_count(self):
        """
        Returns number of PTRs in database
        :return:
        """
        sql = "SELECT COUNT(`ip_address`) FROM `ptrs`"
        self.c.execute(sql)
        return self.c.fetchone()[0]

    def load_ptrs(self):
        """
        Load all PTRs from Database
        :return:
        """
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

    def save_ptr(self, ptr, commit=True):
        """
        Save a single Ptr to database
        :param ptr:
        :return:
        """
        sql = "INSERT OR REPLACE INTO `ptrs` VALUES (" \
              ":ip_address, :hostname, :if_name, :ptr, :ptr_zone, :status, :insert_time" \
              ")"

        data = {
            "ip_address": ptr.ip_int(),
            "hostname": ptr.hostname,
            "if_name": ptr.if_name,
            "ptr": ptr.ptr,
            "ptr_zone": ptr.get_ptr_zone(),
            "status": ptr.status,
            "insert_time": calendar.timegm(ptr.time)
        }
        self.c.execute(sql, data)
        if commit:
            self.connection.commit()

    def save_ptrs(self, ptrs):
        """
        Save multiple Ptrs to database. Uses `save_ptr` method
        :param ptrs:
        :return:
        """
        self.logger.info("Saving %d PTRs to database..." % len(ptrs))
        for ptr in ptrs:
            self.save_ptr(ptrs[ptr], commit=False)
        self.connection.commit()
        self.logger.info("Saved %d PTRs to database." % len(ptrs))

    def delete_ptrs(self, ip_addresses):
        """
        Delete Ptrs for a list of IP addresses
        :param ptrs:
        :return:
        """
        for ip in ip_addresses:
            sql = "DELETE FROM `ptrs` WHERE ip_address == :ip"
            self.c.execute(sql, {"ip": Ptr.get_ip_int(ip)})
        self.connection.commit()

    def delete_stale_ptrs(self):
        """
        Deletes PTR records that are not seen in more than 72h
        :return: Number of deleted rows
        """
        stale_hours = self.config['stale_hours'] if 'stale_hours' in self.config else 72
        time_threshold = time.time() - stale_hours * 3600
        sql = "DELETE FROM `ptrs` WHERE `insert_time` < :time"
        self.c.execute(sql, {"time": time_threshold})
        return self.c.rowcount

    def load_devices(self):
        """
        Not used.
        :return:
        """
        return []
