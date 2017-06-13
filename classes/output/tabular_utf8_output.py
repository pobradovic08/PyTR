# -*- coding: utf-8 -*-

import sys
from classes.output import BaseOutput
from classes import DnsCheck


class TabularUtf8Output(BaseOutput):

    def __init__(self):
        BaseOutput.__init__(self)

    @staticmethod
    def display_detailed(dispatcher):
        pass

    @staticmethod
    def display_summary(dispatcher):
        horizontal_border = (
            '═' * 37,
            '═' * 6,
            '═' * 8,
            '═' * 8,
            '═' * 10,
            '═' * 10,
            '═' * 10,
        )
        output_string = "╒%s╤%s╤%s╤%s╤%s╤%s╤%s╕\n" % horizontal_border
        output_string += "│\033[01m%-37s\033[0;0m│\033[01m\033[92m%-6s\033[0;0m│\033[01m\033[93m%-8s\033[0;0m│" \
                         "\033[01m\033[91m%-8s\033[0;0m│\033[01m\033[90m%-10s\033[0;0m│\033[01m\033[90m%-10s\033[0;0m│"\
                         "\033[01m\033[90m%-10s\033[0;0m│\n" % (
                             'Device',
                             ' OK',
                             ' UPDATE',
                             ' CREATE',
                             ' NO AUTH',
                             ' IGNORED',
                             ' UNKNOWN'
                         )
        output_string += "╞%s╪%s╪%s╪%s╪%s╪%s╪%s╡\n" % horizontal_border

        output_array = []

        for device in dispatcher.devices:
            if not dispatcher.devices[device]:
                continue
            output_array.append(TabularUtf8Output.display_device_summary(dispatcher.devices[device]))

        output_string += ''.join(filter(None, output_array))

        output_string += "╘%s╧%s╧%s╧%s╧%s╧%s╧%s╛\n" % horizontal_border

        return output_string

    @staticmethod
    def display_device_summary(device):
        """
        Returns summary table of all interfaces with number of interfaces and ip address statuses
        :return:
        """
        interfaces = {
            DnsCheck.STATUS_OK: 0,
            DnsCheck.STATUS_NOT_UPDATED: 0,
            DnsCheck.STATUS_NOT_AUTHORITATIVE: 0,
            DnsCheck.STATUS_NOT_CREATED: 0,
            DnsCheck.STATUS_IGNORED: 0,
            DnsCheck.STATUS_UNKNOWN: 0
        }
        for interface in device.interfaces:
            for ip in device.interfaces[interface].ip_addresses:
                interfaces[device.interfaces[interface].ip_addresses[ip]['status']] += 1

        output_string = "│%-37s│ %-15s │ %-17s │ %-17s │ %-19s │ %-19s │ %-19s │\n" % (
            device.hostname,
            TabularUtf8Output._paint_positive_num(interfaces[DnsCheck.STATUS_OK], "\033[92m"),
            TabularUtf8Output._paint_positive_num(interfaces[DnsCheck.STATUS_NOT_UPDATED], "\033[93m"),
            TabularUtf8Output._paint_positive_num(interfaces[DnsCheck.STATUS_NOT_CREATED], "\033[91m"),
            TabularUtf8Output._paint_positive_num(interfaces[DnsCheck.STATUS_NOT_AUTHORITATIVE], "\033[90m"),
            TabularUtf8Output._paint_positive_num(interfaces[DnsCheck.STATUS_IGNORED], "\033[90m"),
            TabularUtf8Output._paint_positive_num(interfaces[DnsCheck.STATUS_UNKNOWN], "\033[90m")
        )

        return output_string

    @staticmethod
    def display_device_detailed(device):
        """
        Returns detailed representation of device status
        Also contains table with all interfaces, current (and new) PTRs, IP addresses
        :return: string
        """
        # Table info header
        # Top border
        output_string = '╒' + '═' * 95 + '╕\n'
        # Ignored device message
        if device.ignored:
            output_string += "│ %-94s│\n│ %-113s│\n│ %-94s│\n" % (
                "",
                "\033[93m\033[07m\033[04m DEVICE ON IGNORE LIST \033[0m",
                ""
            )
        # Device information
        output_string += "│ %-103s│\n" % ("Device:       \033[01m%s\033[0m" % device.hostname)
        output_string += "│ %-103s│\n" % ("Interfaces:   \033[01m%d\033[0m" % device.get_number_of_interfaces())
        output_string += "│ %-103s│\n" % ("IP addresses: \033[01m%d\033[0m " % device.get_number_of_ip_addresses())

        # Print interface table
        if len(device.interfaces):
            # Table interface header
            output_string += '╞' + '═' * 95 + "╡\n"
            output_string += "│%-26s %-45s%-23s│\n" % ('ifName', 'PTR', 'IP address')
            output_string += '╞' + '═' * 95 + "╡\n"
            # Interface details
            # DeviceInterface output list
            interface_rows = []
            for interface in device.interfaces:
                # DeviceInterface output
                interface_row = TabularUtf8Output.display_interface_detailed(device.interfaces[interface])
                # Interface row could be empty if interface status is OK and diff switch is used
                # Avoid adding empty strings to interface_rows list
                if interface_row:
                    interface_rows.append(interface_row)
            # Print info instead of empty table
            if not len(interface_rows):
                output_string += "│ %-94s│\n" % "No PTRs to update"
            else:
                output_string += ''.join(interface_rows)

        # Bottom border
        output_string += '╘' + '═' * 95 + '╛\n'
        return output_string

    @staticmethod
    def display_interface_detailed(device_interface):
        output_array = []
        for ip in device_interface.ip_addresses:
            ip_status = device_interface.ip_addresses[ip]['status']
            if ip_status == DnsCheck.STATUS_OK:
                output_array.append(TabularUtf8Output.print_ok_row(device_interface, ip))
            elif ip_status == DnsCheck.STATUS_NOT_UPDATED:
                output_array.append(TabularUtf8Output.print_not_updated_row(device_interface, ip))
            elif ip_status == DnsCheck.STATUS_NOT_CREATED:
                output_array.append(TabularUtf8Output.print_not_created_row(device_interface, ip))
            elif ip_status == DnsCheck.STATUS_UNKNOWN:
                output_array.append(TabularUtf8Output.print_unknown_row(device_interface, ip))
            elif ip_status == DnsCheck.STATUS_IGNORED:
                output_array.append(TabularUtf8Output.print_ignored_row(device_interface, ip))
            else:
                output_array.append(TabularUtf8Output.print_default_row(device_interface, ip))
        string = ''.join(filter(None, output_array))

        if len(string):
            string += "├" + '─' * 95 + "┤\n"
        return string

    @staticmethod
    def print_ok_row(interface, ip):
        if interface.device.config.diff_only:
            return None
        color = "\033[92m"  # Green
        icon = '■'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            interface.ifName,
            icon,
            interface.get_ptr_for_ip(ip),
            ip
        )

    @staticmethod
    def print_not_updated_row(interface, ip):
        color = "\033[93m"
        icon = '┌'
        output_string = "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            interface.ifName,
            icon,
            interface.ip_addresses[ip]['existing_ptr'],
            ip
        )
        output_string += "│%s%24s └─► %s%-66s\033[0;0m│\n" % (
            color,
            ' ', "\033[01m",  # Bold
            interface.get_ptr_for_ip(ip)  # If IP is from A RR print hostname
        )
        return output_string

    @staticmethod
    def print_not_created_row(interface, ip):
        color = "\033[01m\033[91m"  # Bold red
        icon = '■'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            interface.ifName,
            icon,
            interface.get_ptr_for_ip(ip),
            ip
        )

    @staticmethod
    def print_unknown_row(interface, ip):
        if interface.device.config.diff_only:
            return None
        color = "\033[90m"  # Grey
        icon = ' '
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            interface.ifName,
            icon,
            interface.get_ptr_for_ip(ip),
            ip
        )

    @staticmethod
    def print_ignored_row(interface, ip):
        if interface.device.config.diff_only:
            return None
        color = "\033[90m"  # Grey
        icon = 'i'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            interface.ifName,
            icon,
            interface.get_ptr_for_ip(ip),
            ip
        )

    @staticmethod
    def print_default_row(interface, ip):
        if interface.device.config.diff_only:
            return None
        color = "\033[90m"  # Grey
        icon = '☓'
        return "│%s%-24s %s %-44s %-23s\033[0;0m│\n" % (
            color,
            interface.ifName,
            icon,
            interface.get_ptr_for_ip(ip),
            ip
        )

    @staticmethod
    def print_progress_bar(percent, bar_width = 90):
        completed_bars = int(TabularUtf8Output._lvmap(percent, 0, 100, 0, 90))
        sys.stdout.write("\r│%s│ %3d%%" % (
            str(
                '▌' *  completed_bars +
                ' ' * (90 - completed_bars)
            )
            , percent))
        sys.stdout.flush()

    @staticmethod
    def _paint_positive_num(number, color, default='\033[90m'):
        return "%s%d%s" % (color if number else default, number, '\033[0;0m')
