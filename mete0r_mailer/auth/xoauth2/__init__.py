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
import base64


XOAUTH2_SCOPE = 'https://mail.google.com/'


class XOAuth2(object):

    def __init__(self, credentials_provider):
        self.credentials_provider = credentials_provider

    @classmethod
    def from_settings(cls, settings, prefix):
        credentials_provider = credentials_from_settings(settings, prefix)
        return cls(credentials_provider=credentials_provider)

    def authenticate(self, connection):
        email, access_token = self.credentials_provider.get_credentials()
        s = make_xoauth2_string(email, access_token)
        return connection.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(s))


def make_xoauth2_string(username, access_token):
    return 'user=%s\x01auth=Bearer %s\x01\x01' % (username, access_token)


def credentials_from_settings(settings, prefix):
    credentials_provider = settings.get(prefix + 'credentials')
    prefix += 'credentials.'
    if credentials_provider == 'offline':
        from .offline import Offline
        return Offline.from_settings(settings, prefix)
    elif credentials_provider == 'goauthc':
        from .goauthc import GOAuthc
        return GOAuthc.from_settings(settings, prefix)
    raise ValueError(credentials_provider)
