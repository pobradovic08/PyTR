#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import argparse
from classes.device import Device
from classes.config import Config

reload(sys)
sys.setdefaultencoding('utf8')

parser = argparse.ArgumentParser()
parser.add_argument("hostname", type=str, help="device hostname (FQDN)")
parser.add_argument("-c", "--check", help="check PTRs but don't update them",
                    action="store_true")
parser.add_argument("-d", "--diff", help="show only differences",
                    action="store_true")
parser.add_argument("-t", "--terse", help="terse output - don't display domains",
                    action="store_true")

args = parser.parse_args()

hostname = args.hostname
check_only = args.check
diff_only = args.diff
terse = args.terse

config = Config(check_only=check_only,
                diff_only=diff_only,
                terse=terse)

d = Device(hostname, config)
if d.get_interfaces():
    d.check_ptrs()
    print d
else:
    print "Error connecting to %s" % d.hostname