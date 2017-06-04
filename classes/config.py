#-*- coding: utf-8 -*-
import json


class Config:

    def __init__(self, filename = 'configuration.json'):
        with open(filename) as data_file:
            self.data = json.load(data_file)

    def get_ns_servers(self):
        return self.data['dns']['servers']

    def get_ignore_rules(self):
        return self.data['ignore']