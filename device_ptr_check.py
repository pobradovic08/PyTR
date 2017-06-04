#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import dns.resolver
from classes.device_interface import DeviceInterface
from classes.device import Device
from classes.dns_check import DnsCheck

reload(sys)
sys.setdefaultencoding('utf8')

d = Device('lb-node1', 'nY[7z+dng')
if d.get_interfaces():
    d.check_ptrs()
    print d
else:
    print "Error connecting to %s" % d.hostname