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


logger = logging.getLogger(__name__)


def auth_from_settings(settings, prefix):
    auth = settings.get(prefix + 'auth', 'password')
    child_prefix = prefix + 'auth.'
    logger.info('auth: %s', auth)
    if auth == 'none':
        return None
    elif auth == 'password':
        from .password import Password
        return Password.from_settings(settings, child_prefix)
    elif auth == 'xoauth2':
        from .xoauth2 import XOAuth2
        return XOAuth2.from_settings(settings, child_prefix)
    raise ValueError(auth)
