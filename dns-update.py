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
import sys
import os
import logging
import time

from classes import Config
from classes import Device
from classes import EmailReport
from classes import Dispatcher
from classes.output.tabular_utf8 import TabularUtf8Output

__version__ = '0.1.4'

reload(sys)
sys.setdefaultencoding('utf8')

start_time = time.time()

logging.basicConfig(
    filename=__file__.rstrip('.py|.pyc') + '.log',
    format="%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s",
    level=logging.INFO
)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--check", help="check PTRs but don't update them",
                    action="store_true")
parser.add_argument("-f", "--full", help="show full output not just differences",
                    action="store_true")
parser.add_argument("-t", "--terse", help="terse output - don't display domains",
                    action="store_true")

args = parser.parse_args()

check_only = args.check
diff_only = not args.full
terse = args.terse

ptrs = {}

interface_number = 0
ip_address_number = 0

config = Config(check_only=check_only,
                diff_only=diff_only,
                terse=terse)

dispatcher = Dispatcher(config)
output = TabularUtf8Output()

print "Loaded connectors: %s" % ', '.join(dispatcher.get_connector_list())
dispatcher.load()
total_devices = len(dispatcher.devices)
print "Loaded %d device(s) from %d connector(s)" % (total_devices, len(dispatcher.get_connector_list()))
print "Fetching data from devices:"
# Number of devices we've finished so far
iterator = 0
for device in dispatcher.devices.keys():
    # Create Device instance from hostname
    # dispatcher.devices[device] = Device(device, config, dispatcher.dns)
    # Fetch interfaces
    if dispatcher.devices[device].get_interfaces():
        # Check PTRs
        dispatcher.devices[device].check_ptrs()
        # print output.display_device_detailed(dispatcher.devices[device])
        # print output.display_device_summary(dispatcher.devices[device])

    interface_number += dispatcher.devices[device].get_number_of_interfaces()
    ip_address_number += dispatcher.devices[device].get_number_of_ip_addresses()

    iterator += 1
    # Print progress bar.
    # It will not go to a new line after finishing. Has to be done manually
    percent_complete = int(iterator * 100 / total_devices)
    output.print_progress_bar(percent_complete)
    ptrs.update(dispatcher.devices[device].get_ptrs())

# New line to fix the progress bar \r magic.
print

print output.display_summary(dispatcher)
if not check_only:
    print "Saving %d PTRs..." % len(ptrs),
    dispatcher.save_ptrs(ptrs)
    print " done."
    email = EmailReport(
        config=config,
        interface_number=interface_number,
        ip_number=ip_address_number,
        delta_time=time.time() - start_time,
        connector_number=len(dispatcher.get_connector_list()),
        app_name=os.path.basename(__file__),
        app_version=__version__
    )
    email.generate_report(ptrs=ptrs)
