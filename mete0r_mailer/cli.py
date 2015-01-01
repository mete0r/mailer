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
from email.header import Header
from email.MIMEText import MIMEText
from email.utils import getaddresses
import json
import logging
import sys

from repoze.sendmail.queue import QueueProcessor
import transaction

from .connector import connector_from_settings
from .delivery import delivery_from_settings
from .mailer import SMTPConnectionMailer
from .mailer import connect


logger = logging.getLogger(__name__)


def qb():
    logging.basicConfig(level=logging.INFO)
    with file(sys.argv[1]) as f:
        settings = json.load(f)
    connector = connector_from_settings(settings, prefix='qb.')
    mailqueue = settings.get('qb.mailqueue', 'Maildir')
    with connect(connector) as connection:
        mailer = SMTPConnectionMailer(connection)
        qp = QueueProcessor(mailer, mailqueue)
        qp.send_messages()


def mail():
    logging.basicConfig(level=logging.INFO)
    with file(sys.argv[1]) as f:
        settings = json.load(f)

    delivery = delivery_from_settings(settings, 'mail.')

    with transaction.manager:
        from_addr = sys.argv[2]
        to_addrs = sys.argv[3:] or [from_addr]
        subject = raw_input('Subject: ')
        sys.stderr.write('Content:\n')
        content = sys.stdin.read()

        message = MIMEText(content, 'plain', 'UTF-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = from_addr
        message['To'] = ', '.join(to_addrs)

        deliver(delivery, message)


def deliver(delivery, message):
    tos = message.get_all('to', [])
    tos = getaddresses(tos)
    tos = [addr for _, addr in tos if addr]
    delivery.send(message['From'], tos, message)
