#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
from classes import Dispatcher
from classes import Config
from classes import Device

from classes.output.tabular_utf8_output import TabularUtf8Output

reload(sys)
sys.setdefaultencoding('utf8')

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

config = Config(check_only=check_only,
                diff_only=diff_only,
                terse=terse)

dispatcher = Dispatcher(config)

output = TabularUtf8Output()

print "Loaded connectors: %s" % ', '.join(dispatcher.get_connector_list())
dispatcher.load()
total_devices = len(dispatcher.devices)
print "Loaded %d device(s) from %d connector(s)" % (total_devices, len(dispatcher.get_connector_list()))

# Number of devices we've finished so far
iterator = 0
for device in dispatcher.devices.keys():
    # Create Device instance from hostname
    dispatcher.devices[device] = Device(device, config, dispatcher.dns)
    # Fetch interfaces
    if dispatcher.devices[device].get_interfaces():
        # Check PTRs
        dispatcher.devices[device].check_ptrs()
        # print output.display_device_detailed(dispatcher.devices[device])
        # print output.display_device_summary(dispatcher.devices[device])

    iterator += 1
    # Print progress bar.
    # It will not go to a new line after finishing. Has to be done manually
    percent_complete = int(iterator*100/total_devices)
    output.print_progress_bar(percent_complete)

# New line to fix the progress bar \r magic.
print

print output.display_summary(dispatcher)
