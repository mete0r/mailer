# -*- coding: utf-8 -*-
#
#   mete0r.mailer : mete0r's mailer
#   Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from smtplib import SMTP
import logging

from .auth import auth_from_settings


logger = logging.getLogger(__name__)


def connector_from_settings(settings, prefix):
    connector = settings.get(prefix + 'connector')
    logger.info('connector: %s', connector)
    if connector == 'SMTPConnector':
        return SMTPConnector.from_settings(settings, prefix + 'connector.')
    elif connector == 'GMailConnector':
        return GMailConnector.from_settings(settings, prefix + 'connector.')
    raise ValueError(connector)


class SMTPConnector(object):

    def __init__(self, hostname='localhost', port=25, auth=None,
                 timeout=10, debug_smtp=False):

        self.auth = auth
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
        self.debug_smtp = debug_smtp

    @classmethod
    def from_settings(cls, settings, prefix='smtp_connector.'):
        auth = auth_from_settings(settings, prefix)
        hostname = settings.get(prefix + 'hostname', 'localhost')
        port = int(settings.get(prefix + 'port', 25))
        timeout = int(settings.get(prefix + 'timeout', 10))
        return cls(auth=auth,
                   hostname=hostname,
                   port=port,
                   timeout=timeout)

    def __repr__(self):
        return '<%s %s:%s %s>' % (
            type(self).__name__, self.hostname, self.port, self.auth)

    def connect(self):
        logger.info('%r: Connecting ...', self)
        connection = SMTP(self.hostname, str(self.port), timeout=self.timeout)
        try:
            connection.set_debuglevel(self.debug_smtp)

            connection.ehlo_or_helo_if_needed()
            if connection.does_esmtp:
                logger.info('%r: EHLO resp: %s', self, connection.ehlo_resp)

            if connection.has_extn('starttls'):
                connection.starttls()
                connection.ehlo()
                logger.info('%r: EHLO resp: %s', self, connection.ehlo_resp)

            if self.auth:
                self.auth.authenticate(connection)
            return connection
        except:
            try:
                connection.quit()
            except:
                connection.close()
            raise


class GMailConnector(SMTPConnector):

    @classmethod
    def from_settings(cls, settings, prefix='gmail_connector.'):
        auth = auth_from_settings(settings, prefix)
        hostname = settings.get(prefix + 'hostname', 'smtp.gmail.com')
        port = int(settings.get(prefix + 'port', 587))
        timeout = int(settings.get(prefix + 'timeout', 10))
        return cls(auth=auth,
                   hostname=hostname,
                   port=port,
                   timeout=timeout)
