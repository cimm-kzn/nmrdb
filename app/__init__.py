# -*- coding: utf-8 -*-
#
# Copyright 2015 Ramil Nugmanov <stsouko@live.ru>
# This file is part of nmrdb.
#
# nmrdb is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
__author__ = 'stsouko'
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_login import LoginManager
from flask.ext.bcrypt import Bcrypt

login_manager = LoginManager()


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    login_manager.init_app(app)
    bcrypt = Bcrypt(app)
    login_manager.login_view = 'login'
    return app, bcrypt


app, bcrypt = create_app(configfile='config.ini')

from app.models import NmrDB
db = NmrDB()

from app import views


