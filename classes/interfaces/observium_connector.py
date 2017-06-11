#-*- coding: utf-8 -*-

from classes.interfaces.base import BaseConnector
import MySQLdb


class ObserviumConnector(BaseConnector):

    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        mysql_data = self.config['mysql']
        self.db = MySQLdb.connect(**mysql_data)
        self.c = self.db.cursor()

    def load_devices(self):
        """
        Select all devices from observium database that are not disabled
        :return:
        """
        device_list = []
        self.c.execute("SELECT hostname FROM devices WHERE disabled = 0")
        for hostname in self.c.fetchall():
            device_list.append(hostname[0])
        return device_list

    def save_ptr(self, ptr):
        """
        No need to update PTR in Observium
        :param ptr:
        :return:
        """
        pass