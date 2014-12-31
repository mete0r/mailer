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
import subprocess
import json


XOAUTH2_SCOPE = 'https://mail.google.com/'


class XOAuth2GOAuthc(object):

    def authorize(self, email):
        cmd = ['goauthc', 'token', 'acquire', '--user', email, XOAUTH2_SCOPE]
        result = subprocess.check_output(cmd)
        credentials = json.loads(result)
        return credentials['access_token']
