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



class BaseOutput:
    def __init__(self):
        pass

    @staticmethod
    def display_summary(dispatcher):
        raise NotImplementedError

    @staticmethod
    def display_detailed(dispatcher):
        raise NotImplementedError

    @staticmethod
    def display_device_summary(device):
        raise NotImplementedError

    @staticmethod
    def display_device_detailed(device):
        raise NotImplementedError

    @staticmethod
    def display_interface_detailed(device_interface):
        raise NotImplementedError

    @staticmethod
    def _lvmap(value, x_start, x_end, u_start, u_end):
        """
        Linear vector mapping
        :param value:  Value in [x_start, x_end] (converted to float)
        :param x_start: Start value of base range
        :param x_end:  End value of base range
        :param u_start: Start value of mapped range
        :param u_end: End value of mapped range
        :return:
        """
        return u_start + ((u_end - u_start) * ((float(value) - x_start) / (x_end - x_start)))