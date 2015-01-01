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
import logging

from repoze.sendmail.delivery import DirectMailDelivery
from repoze.sendmail.delivery import QueuedMailDelivery

from .mailer import SMTPConnectMailer


logger = logging.getLogger(__name__)


def delivery_from_settings(settings, prefix):
    delivery = settings.get(prefix + 'delivery')
    if delivery == 'direct':
        return direct_delivery_from_settings(settings, prefix +
                                             'delivery.direct.')
    elif delivery == 'queued':
        return queued_delivery_from_settings(settings, prefix +
                                             'delivery.queued.')


def direct_delivery_from_settings(settings, prefix=''):
    mailer = SMTPConnectMailer.from_settings(settings, prefix +
                                             'mailer.')
    return DirectMailDelivery(mailer)


def queued_delivery_from_settings(settings, prefix=''):
    mailqueue_path = settings.get(prefix + 'mailqueue_path', 'Maildir')
    return QueuedMailDelivery(mailqueue_path)
