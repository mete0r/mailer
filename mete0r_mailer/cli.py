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
from contextlib import closing
from email.header import Header
from email.message import Message
from email.utils import getaddresses
import json
import logging
import sys

from repoze.sendmail.delivery import QueuedMailDelivery
from repoze.sendmail.queue import QueueProcessor

from .connector import connector_from_settings
from .mailer import SMTPLazyConnectMailer


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    with file(sys.argv[1]) as f:
        settings = json.load(f)
    connector = connector_from_settings(settings, prefix='')
    with closing(SMTPLazyConnectMailer(connector)) as mailer:
        qp = QueueProcessor(mailer, 'Maildir')
        qp.send_messages()


def populate_test():
    import transaction
    transaction.manager.begin()
    try:
        delivery = QueuedMailDelivery('Maildir')

        message = Message()
        message['Subject'] = Header('테스트', 'utf-8')
        message['From'] = sys.argv[1]
        addresses = sys.argv[2:]
        message['To'] = ', '.join(addresses)
        deliver(delivery, message)
        transaction.manager.commit()
    except:
        transaction.manager.abort()
        raise


def deliver(delivery, message):
    tos = message.get_all('to', [])
    tos = getaddresses(tos)
    tos = [addr for _, addr in tos if addr]
    delivery.send(message['From'], tos, message)
