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
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from app.models import NmrDB
from app.config import SECRET_KEY
from flask_nav import Nav
from app.navbar import Customrenderer
from flask_nav import register_renderer




def create_app():
    fapp = Flask(__name__)
    fapp.config['SECRET_KEY'] = SECRET_KEY

    lm = LoginManager()
    lm.init_app(fapp)
    lm.login_view = 'login'

    nav = Nav()
    nav.init_app(fapp)

    Bootstrap(fapp)
    register_renderer(fapp, 'myrenderer', Customrenderer)
    return fapp, lm, nav


print('INIT APP')
app, login_manager, nav = create_app()
db = NmrDB()

from app import views
