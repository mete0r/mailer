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
import urllib

import requests


class Offline(object):

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
        email = settings.get(prefix + 'email')
        client_secret_path = settings.get(prefix + 'client_secret_path')
        with file(client_secret_path) as f:
            client_credentials = json.load(f)
            client_credentials = client_credentials.values()[0]
        refresh_token_path = settings.get(prefix + 'refresh_token_path')
        with file(refresh_token_path) as f:
            token_credentials = json.load(f)
        return cls(client_id=client_credentials['client_id'],
                   client_secret=client_credentials['client_secret'],
                   email=email,
                   refresh_token=token_credentials['refresh_token'])

    @property
    def is_expired(self):
        authorized = self.authorized
        expires_at = authorized['expires_at']
        access_token = authorized['access_token']

        if access_token is None or expires_at is None:
            return True
        return expires_at < datetime.now()

    def get_credentials(self):
        if self.is_expired:
            credentials = self.refresh(self.refresh_token)
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

        query = urllib.urlencode(query)
        r = requests.post(endpoint, data=query, headers={
            'content-type': 'application/x-www-form-urlencoded'
        })
        resp = r.json()
        if 'error' in resp:
            raise RuntimeError(resp['error'])
        return resp
