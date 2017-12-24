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
from datetime import datetime
import smtplib
from email.mime.text import MIMEText


class EmailReport:
    def __init__(self):
        """
        """
        self.logger = logging.getLogger('dns_update.email_report')
        self.email_server = 'smtp.vektor.net'
        self.email_to = ['pavle.obradovic@radijusvektor.rs']
        self.email_from = 'pajaja@pavle.vektor.net'
        self.email_subject = "PyTR update report - %s" % datetime.now().strftime('%d.%m.%Y %H:%M')
        self.logger.info("Emails receiving report: %s" % ",".join(self.email_to))


    def send_report(self):
        self.msg = MIMEText("LALALALAL")
        self.msg['Subject'] = self.email_subject
        self.msg['From'] = self.email_from
        self.msg['To'] = ','.join(self.email_to)

        try:
            self.logger.debug("Connecting to %s" % self.email_server)
            s = smtplib.SMTP(self.email_server)
            self.logger.debug("Sending email...")
            s.sendmail(self.email_from, [ self.email_to ], self.msg.as_string())
            self.logger.debug("Email sent.")
            s.quit()
        except smtplib.SMTPException as e:
            self.logger.error(e)
