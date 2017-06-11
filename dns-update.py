#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import argparse
from classes.dispatcher import Dispatcher
from classes.config import Config
from classes.device import Device

reload(sys)
sys.setdefaultencoding('utf8')

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--check", help="check PTRs but don't update them",
                    action="store_true")
parser.add_argument("-d", "--diff", help="show only differences",
                    action="store_true")
parser.add_argument("-t", "--terse", help="terse output - don't display domains",
                    action="store_true")

args = parser.parse_args()

check_only = args.check
diff_only = args.diff
terse = args.terse

config = Config(check_only=check_only,
                diff_only=diff_only,
                terse=terse)

dispatcher = Dispatcher(config)

print "Loaded connectors: %s" % ', '.join(dispatcher.get_connector_list())
dispatcher.load()
print "Loaded %d device(s) from %d connector(s)" % (len(dispatcher.devices), len(dispatcher.get_connector_list()))

go_trough = 2

for device in dispatcher.devices:
    dispatcher.devices[device] = Device(device, config)
    if dispatcher.devices[device].get_interfaces():
        print dispatcher.devices[device]

    go_trough -= 1
    if go_trough <= 0:
        exit(1)