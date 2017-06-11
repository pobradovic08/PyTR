#-*- coding: utf-8 -*-

from classes.interfaces.base_connector import BaseConnector
import MySQLdb


class ObserviumConnector(BaseConnector):

    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        mysql_data = self.config['mysql']
        self.db = MySQLdb.connect(**mysql_data)
        self.c = self.db.cursor()

    def load_devices(self):
        device_list = []
        self.c.execute("SELECT hostname FROM devices")
        for hostname in self.c.fetchall():
            device_list.append(hostname[0])
        return device_list
