#!/usr/bin/python
# -*- coding: utf-8 -*-
# DNS PTR updater
# Copyright (C) 2017  Pavle Obradovic (pajaja)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import argparse
import logging

from classes import Device
from classes import Config
from classes import DnsCheck

from classes.output.tabular_utf8_output import TabularUtf8Output

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(
    filename=__file__.rstrip('.py|.pyc') + '.log',
    format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
    level=logging.DEBUG
)

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

dns = DnsCheck(config=config)
output = TabularUtf8Output()

fqdn = dns.get_fqdn(hostname)
if fqdn:
    d = Device(hostname=fqdn, config=config)
    if d.get_interfaces():
        d.check_ptrs()
        print output.display_device_detailed(d)
    else:
        print "Error connecting to %s" % d.hostname
