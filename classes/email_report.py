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


import logging
import os
from datetime import datetime
import smtplib
from jinja2 import Environment
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

__version__ = '0.1.2'


class EmailReport:
    def __init__(self,
                 config=None,
                 device=None,
                 interface_number=None,
                 ip_number=None,
                 delta_time=None,
                 connector_number=None,
                 app_name=None,
                 app_version=__version__):
        """
        """
        self.logger = logging.getLogger('dns_update.email_report')
        self.config = config if config else Config()
        self.base_path = os.path.dirname(os.path.abspath(__file__)) + '/../templates/email/'

        self.device = device
        self.interface_number = interface_number
        self.delta_time = delta_time
        self.connector_number = connector_number
        self.ip_number = ip_number
        self.app_name = app_name
        self.app_version = app_version

        self.email_server = config.get_email_server()
        self.email_to = config.get_email_to()
        self.email_from = config.get_email_from()
        self.email_time = datetime.now().strftime('%d.%m.%Y %H:%M')

        self.email_subject = "PyTR update report - %s" % self.email_time
        self.logger.info("Emails receiving report: %s" % ",".join(self.email_to))

        self.msg = None

    def send_report(self):
        if self.msg:
            try:
                self.logger.debug("Connecting to %s" % self.email_server)
                s = smtplib.SMTP(self.email_server)
                self.logger.debug("Sending email...")
                s.sendmail(self.email_from, [self.email_to], self.msg.as_string())
                self.logger.debug("Email sent.")
                s.quit()
            except smtplib.SMTPException as e:
                self.logger.error(e)

    def generate_report(self, ptrs):
        lines = [self._header()]
        if len(ptrs):
            lines.append("\n\n\n\n")
        else:
            lines.append("\n\nNo changes detected.\n\n")
        lines.append(self._footer())

        # Html part
        self._generate_html(ptrs)
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = self.email_subject
        self.msg['From'] = self.email_from
        self.msg['To'] = ','.join(self.email_to)
        self.msg.attach(MIMEText("\n".join(lines), 'text'))
        self.msg.attach(MIMEText(self.html, 'html'))
        self.send_report()

    def _generate_error(self, message):
        """
        Builds error message HTML from template
        :param message:
        :return:
        """
        error_raw = self.base_path + 'error.html'
        with open(error_raw) as error_template_file:
            error_template =  error_template_file.read()

        error_html = Environment().from_string(error_template).render(
            error_message=message
        )

        return error_html

    def _generate_html(self, ptrs):

        html_base_raw = self.base_path + 'base.html'
        html_report_raw = self.base_path + 'report.html'
        updated_rows_file = self.base_path + 'updated_rows.html'

        with open(html_base_raw) as html_base_template:
            self.html_base_raw = html_base_template.read()

        with open(html_report_raw) as html_report_template:
            self.html_report_raw = html_report_template.read()

        with open(updated_rows_file) as updated_rows_template:
            self.html_updated_rows_raw = updated_rows_template.read()

        self.html_updated_rows = Environment().from_string(self.html_updated_rows_raw).render(
            ptrs=self._prepare_ptrs(ptrs)
        )

        self.html_content = Environment().from_string(self.html_report_raw).render(
            time=self.email_time,
            updated_rows=self.html_updated_rows,
            ptrs_updated=True if len(ptrs) else False,
            hostname=self.device,
            interface_number=self.interface_number,
            ip_number=self.ip_number,
            delta_time=self.delta_time,
            connectors=self.connector_number,
            app_name=self.app_name,
            app_version=self.app_version
        )

        self.html = Environment().from_string(self.html_base_raw).render(
            content=self.html_content
        )

    def _prepare_ptrs(self, ptrs):
        prepared_ptrs = []
        for ptr in ptrs:
            prepared_ptrs.append({
                "ip": "%s" % ptrs[ptr].ip_address,
                "status": ptrs[ptr].status,
                "ptr": ptrs[ptr].ptr
            })
        return prepared_ptrs

    def _footer(self):
        return """
---
PyTR - DNS Updater
https://github.com/pobradovic08/PyTR
Copyright (C) 2017  Pavle Obradovic (pajaja)
https://www.gnu.org/licenses/gpl-3.0.en.html
        """
