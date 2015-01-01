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
import json
import logging
import subprocess
import urllib

import requests


logger = logging.getLogger(__name__)


XOAUTH2_SCOPE = 'https://mail.google.com/'


def authorizer_from_settings(settings, prefix):
    authorizer_type = settings.get(prefix + 'authorizer')
    logger.info('authorizer: %s', authorizer_type)
    if authorizer_type == 'XOAuth2GOAuthc':
        return XOAuth2GOAuthc.from_settings(settings)
    elif authorizer_type == 'XOAuth2Offline':
        return XOAuth2Offline.from_settings(settings)
    raise ValueError(authorizer_type)


class XOAuth2GOAuthc(object):

    def __init__(self, goauthc_path='goauthc'):
        self.goauthc_path = goauthc_path

    @classmethod
    def from_settings(cls, settings):
        goauthc_path = settings.get('xoauth2_goauthc.goauthc_path',
                                    'goauthc')
        return cls(goauthc_path)

    def authorize(self, email):
        cmd = [self.goauthc_path, 'token', 'acquire',
               '--user', email, XOAUTH2_SCOPE]
        result = subprocess.check_output(cmd)
        credentials = json.loads(result)
        return credentials['access_token']


class XOAuth2Offline(object):

    def __init__(self, client_id, client_secret, accounts):
        self.client_id = client_id
        self.client_secret = client_secret
        self.accounts = accounts
        self.authorized = {}
        for email in accounts:
            self.authorized[email] = {
                'expires_at': None,
                'access_token': None,
            }

    @classmethod
    def from_settings(cls, settings):
        path = settings.get('xoauth2_offline.credentials_path')
        with file(path) as f:
            d = json.load(f)
        return cls(client_id=d['client_id'],
                   client_secret=d['client_secret'],
                   accounts=d['accounts'])

    def get_refresh_token(self, email):
        account = self.accounts[email]
        return account['refresh_token']

    def is_expired(self, email):
        authorized = self.authorized[email]
        expires_at = authorized['expires_at']
        access_token = authorized['access_token']

        if access_token is None or expires_at is None:
            return True
        return expires_at < datetime.now()

    def authorize(self, email):
        if self.is_expired(email):
            refresh_token = self.accounts[email]['refresh_token']
            credentials = self.refresh(refresh_token)
            logger.info('credentials: %s',
                        json.dumps(credentials, sort_keys=True, indent=2))
            expires_in = int(credentials['expires_in'])
            self.authorized[email] = {
                'access_token': credentials['access_token'],
                'expires_at': datetime.now() + timedelta(seconds=expires_in),
            }
        return self.authorized[email]['access_token']

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
