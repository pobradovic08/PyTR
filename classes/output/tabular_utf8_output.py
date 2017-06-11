# -*- coding: utf-8 -*-

from classes.output.base import Base
from classes.dns_check import DnsCheck


class TabularUtf8Output(Base):

    @staticmethod
    def display_device_detailed(device):
        """
        Returns string representation of device status
        Also contains table with all interfaces, current (and new) PTRs, IP addresses
        :return:
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
