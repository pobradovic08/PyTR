# -*- coding: utf-8 -*-

from classes.interfaces.base import BaseConnector
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
