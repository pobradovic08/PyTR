#-*- coding: utf-8 -*-

from classes.interfaces.base_connector import BaseConnector
import mysql.connector
from mysql.connector import errorcode


class ObserviumConnector(BaseConnector):

    def __init__(self, dispatcher):
        BaseConnector.__init__(self, dispatcher)
        mysql_data = self.config['mysql']
        try:
            self.db = mysql.connector.connect(**mysql_data)
        except mysql.connector.Error as err:
            # TODO: Real logging...
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Wrong username/password.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("No database `%s`." % mysql_data['database'])
            else:
                print(err)
            exit(1)

    def load_devices(self):

        pass
