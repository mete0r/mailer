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
from email.message import Message
import logging

from zope.interface import implementer
from repoze.sendmail.encoding import encode_message
from repoze.sendmail.interfaces import IMailer
from repoze.sendmail._compat import SSLError


logger = logging.getLogger(__name__)


@implementer(IMailer)
class SMTPConnectionMailer(object):

    def __init__(self, connection):
        self.connection = connection

    def send(self, fromaddr, toaddrs, message):
        if not isinstance(message, Message):
            raise ValueError(
                'Message must be instance of email.message.Message')
        message = encode_message(message)
        logger.info('Sending message...')
        self.connection.sendmail(fromaddr, toaddrs, message)

    def close(self):
        logger.info('Closing connection...')
        try:
            self.connection.quit()
        except SSLError:
            # something weird happened while quiting
            self.connection.close()


@implementer(IMailer)
class SMTPLazyConnectMailer(object):

    def __init__(self, connector):
        self.connector = connector
        self._connectionmailer = None

    @property
    def connectionmailer(self):
        if self._connectionmailer is None:
            logger.info('Getting new connection...')
            connection = self.connector.connect()
            self._connectionmailer = SMTPConnectionMailer(connection)
        return self._connectionmailer

    def send(self, fromaddr, toaddrs, message):
        return self.connectionmailer.send(fromaddr, toaddrs, message)

    def close(self):
        if self._connectionmailer:
            self._connectionmailer.close()
