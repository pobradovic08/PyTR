#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import dns.resolver
from classes.device_interface import DeviceInterface
from classes.device import Device
from classes.config import Config

reload(sys)
sys.setdefaultencoding('utf8')

config = Config()

d = Device('l3-sc-5', config)
if d.get_interfaces():
    d.check_ptrs()
    print d
else:
    print "Error connecting to %s" % d.hostname