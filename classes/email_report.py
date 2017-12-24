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


class EmailReport:
    def __init__(self, config=None, device=None):
        """
        """
        self.logger = logging.getLogger('dns_update.email_report')
        self.config = config if config else Config()
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

    def _header(self):
        return """
        """

    def generate_report(self, ptrs):
        lines = [self._header()]
        if len(ptrs):
            lines.append("\n\n\n\n")
        else:
            lines.append("\n\nNo changes detected.\n\n")
        lines.append(self._footer())
        self._generate_html(ptrs)
        # self.msg = MIMEText("\n".join(lines))
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = self.email_subject
        self.msg['From'] = self.email_from
        self.msg['To'] = ','.join(self.email_to)
        self.msg.attach(MIMEText("\n".join(lines), 'text'))
        self.msg.attach(MIMEText(self.html, 'html'))
        self.send_report()

    def _generate_html(self, ptrs):

        base_path = os.path.dirname(os.path.abspath(__file__)) + '/../templates/email/'

        html_template_file = base_path + 'report.html'
        up_to_date_row_file = base_path + 'up_to_date_row.html'
        updated_rows_file = base_path + 'updated_rows.html'

        with open(html_template_file) as html_template:
            self.html_raw = html_template.read()

        with open(up_to_date_row_file) as up_to_date_row_template:
            self.html_up_to_date_row_raw = up_to_date_row_template.read()

        with open(updated_rows_file) as updated_rows_template:
            self.html_updated_rows_raw = updated_rows_template.read()

        self.html_up_to_date_row = Environment().from_string(self.html_up_to_date_row_raw).render()
        self.html_updated_rows = Environment().from_string(self.html_updated_rows_raw).render(
            ptrs=self._prepare_ptrs(ptrs)
        )

        self.html = Environment().from_string(self.html_raw).render(
            time=self.email_time,
            up_to_date_row=self.html_up_to_date_row,
            updated_rows=self.html_updated_rows,
            ptrs_updated=True if len(ptrs) else False
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
