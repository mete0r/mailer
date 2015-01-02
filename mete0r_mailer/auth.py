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
from datetime import datetime
from datetime import timedelta
import base64
import json
import logging
import subprocess
import urllib

import requests


logger = logging.getLogger(__name__)


XOAUTH2_SCOPE = 'https://mail.google.com/'


def authenticator_from_settings(settings, prefix):
    authenticator = settings.get(prefix + 'authenticator')
    child_prefix = prefix + 'authenticator.'
    logger.info('authenticator: %s', authenticator)
    if authenticator == 'Login':
        return Login.from_settings(settings, child_prefix)
    elif authenticator == 'XOAuth2':
        return XOAuth2.from_settings(settings, child_prefix)
    raise ValueError(authenticator)


class Login(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    def from_settings(cls, settings, prefix=''):
        return cls(settings.get(prefix + 'username'),
                   settings.get(prefix + 'password'))

    def authenticate(self, connection):
        connection.login(self.username, self.password)


class XOAuth2(object):

    def __init__(self, authorizer):
        self.authorizer = authorizer

    @classmethod
    def from_settings(cls, settings, prefix):
        authorizer = cls.authorizer_from_settings(settings, prefix)
        return cls(authorizer=authorizer)

    @classmethod
    def authorizer_from_settings(cls, settings, prefix):
        authorizer = settings.get(prefix + 'authorizer')
        prefix += 'authorizer.'
        if authorizer == 'XOAuth2GOAuthc':
            return XOAuth2GOAuthc.from_settings(settings, prefix)
        elif authorizer == 'XOAuth2Offline':
            return XOAuth2Offline.from_settings(settings, prefix)
        raise ValueError(authorizer)

    def authenticate(self, connection):
        email, access_token = self.authorizer.authorize()
        s = make_xoauth2_string(email, access_token)
        return connection.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(s))


def make_xoauth2_string(username, access_token):
    return 'user=%s\x01auth=Bearer %s\x01\x01' % (username, access_token)


class XOAuth2GOAuthc(object):

    def __init__(self, email, goauthc_path='goauthc'):
        self.email = email
        self.goauthc_path = goauthc_path

    @classmethod
    def from_settings(cls, settings, prefix='xoauth2_goauthc.'):
        email = settings.get(prefix + 'email')
        if email is None:
            raise RuntimeError(prefix + 'email is required')
        goauthc_path = settings.get(prefix + 'goauthc_path',
                                    'goauthc')
        return cls(email, goauthc_path)

    def authorize(self):
        cmd = [self.goauthc_path, 'token', 'acquire',
               '--user', self.email, XOAUTH2_SCOPE]
        result = subprocess.check_output(cmd)
        credentials = json.loads(result)
        return self.email, credentials['access_token']


class XOAuth2Offline(object):

    def __init__(self, client_id, client_secret, email, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.email = email
        self.refresh_token = refresh_token
        self.authorized = {
            'expires_at': None,
            'access_token': None,
        }

    @classmethod
    def from_settings(cls, settings, prefix='xoauth2_offline.'):
        path = settings.get(prefix + 'credentials_path')
        with file(path) as f:
            d = json.load(f)
        return cls(client_id=d['client_id'],
                   client_secret=d['client_secret'],
                   email=d['email'],
                   refresh_token=d['refresh_token'])

    @property
    def is_expired(self):
        authorized = self.authorized
        expires_at = authorized['expires_at']
        access_token = authorized['access_token']

        if access_token is None or expires_at is None:
            return True
        return expires_at < datetime.now()

    def authorize(self):
        if self.is_expired:
            credentials = self.refresh(self.refresh_token)
            logger.info('credentials: %s',
                        json.dumps(credentials, sort_keys=True, indent=2))
            expires_in = int(credentials['expires_in'])
            self.authorized = {
                'access_token': credentials['access_token'],
                'expires_at': datetime.now() + timedelta(seconds=expires_in),
            }
        return self.email, self.authorized['access_token']

    def refresh(self, refresh_token):
        endpoint = 'https://accounts.google.com/o/oauth2/token'
        query = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }

        logger.info('google refresh_token query: %s',
                    json.dumps(query, indent=2, sort_keys=True))

        query = urllib.urlencode(query)
        r = requests.post(endpoint, data=query, headers={
            'content-type': 'application/x-www-form-urlencoded'
        })
        resp = r.json()
        if 'error' in resp:
            raise RuntimeError(resp['error'])
        return resp
