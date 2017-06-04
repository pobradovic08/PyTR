#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import dns.resolver
from classes.dev_interface import DevInterface
from classes.dev import Dev
from classes.dns_check import DnsCheck

reload(sys)
sys.setdefaultencoding('utf8')

d = Dev('lb-node1', 'nY[7z+dng')
if d.get_interfaces():
    d.check_ptrs()
    print d
else:
    print "Error connecting to %s" % d.hostname