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


import argparse
import logging
import sys
import time

from classes import Config
from classes import Device
from classes import DnsCheck
from classes import Dispatcher
from classes import EmailReport
from classes.output.tabular_utf8 import TabularUtf8Output

__version__ = '0.1.2'

reload(sys)
sys.setdefaultencoding('utf8')

start_time = time.time()

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

dispatcher = Dispatcher(config)

print "Loaded connectors: %s" % ', '.join(dispatcher.get_connector_list())

dns = DnsCheck(config=config)
output = TabularUtf8Output()

fqdn = dns.get_fqdn(hostname)
if fqdn:
    d = Device(hostname=fqdn, config=config)
    if d.get_interfaces():
        d.check_ptrs()
        print output.display_device_detailed(d)

        # Filter all PTRs that don't have status equal to STATUS_NOT_UPDATED or STATUS_NOT_CREATED
        ptrs_for_update = {
            k: v for k, v in d.get_ptrs().iteritems()
            if v.status in
               (DnsCheck.STATUS_NOT_UPDATED, DnsCheck.STATUS_NOT_CREATED)
        }
        #print ptrs_for_update
        dispatcher.save_ptrs(ptrs_for_update)

        email = EmailReport(
            config=config,
            device=fqdn,
            interface_number=d.get_number_of_interfaces(),
            ip_number=d.get_number_of_ip_addresses(),
            delta_time=time.time() - start_time,
            connector_number=len(dispatcher.get_connector_list()),
            app_name='device_ptr_check',
            app_version=__version__
        )
        email.generate_report(ptrs_for_update)
    else:
        print "Error connecting to %s" % d.hostname
else:
    print "Error resolving %s" % hostname
