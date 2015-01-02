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

    def __init__(self, authorizer):
        self.authorizer = authorizer

    @classmethod
    def from_settings(cls, settings, prefix):
        authorizer = authorizer_from_settings(settings, prefix)
        return cls(authorizer=authorizer)

    def authenticate(self, connection):
        email, access_token = self.authorizer.authorize()
        s = make_xoauth2_string(email, access_token)
        return connection.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(s))


def make_xoauth2_string(username, access_token):
    return 'user=%s\x01auth=Bearer %s\x01\x01' % (username, access_token)


def authorizer_from_settings(settings, prefix):
    authorizer = settings.get(prefix + 'authorizer')
    prefix += 'authorizer.'
    if authorizer == 'offline':
        from .offline import Offline
        return Offline.from_settings(settings, prefix)
    elif authorizer == 'goauthc':
        from .goauthc import GOAuthc
        return GOAuthc.from_settings(settings, prefix)
    raise ValueError(authorizer)
