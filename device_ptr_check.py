#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import argparse

from classes import Device
from classes import Config
from classes import DnsCheck

from classes.output.tabular_utf8_output import TabularUtf8Output

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

dns = DnsCheck(config)
output = TabularUtf8Output()

fqdn = dns.get_fqdn(hostname)
if fqdn:
    d = Device(fqdn, config)
    if d.get_interfaces():
        d.check_ptrs()
        print output.display_device_detailed(d)
    else:
        print "Error connecting to %s" % d.hostname