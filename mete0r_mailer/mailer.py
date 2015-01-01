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
from contextlib import contextmanager
from email.message import Message
import logging

from zope.interface import implementer
from repoze.sendmail.encoding import encode_message
from repoze.sendmail.interfaces import IMailer
from repoze.sendmail._compat import SSLError

from .connector import connector_from_settings


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


@implementer(IMailer)
class SMTPConnectMailer(object):

    def __init__(self, connector):
        self.connector = connector

    @classmethod
    def from_settings(cls, settings, prefix='smtp_connect_mailer.'):
        connector = connector_from_settings(settings, prefix)
        return cls(connector)

    def send(self, fromaddr, toaddrs, message):
        with connect(self.connector) as connection:
            connectionmailer = SMTPConnectionMailer(connection)
            return connectionmailer.send(fromaddr, toaddrs, message)


@contextmanager
def connect(connector):
    logger.info('Getting new connection...')

    connection = connector.connect()
    try:
        yield connection
    finally:
        logger.info('Closing connection...')
        try:
            connection.quit()
        except SSLError:
            # something weird happened while quiting
            connection.close()
