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
from flask import render_template, session, redirect, url_for
from app import app
from app.localization import eng, rus
from app import db
from app.forms import Signin, Login, Newlab
from app.logins import load_user, User
from flask_login import login_user, login_required, logout_user, current_user


def getavatars():
    if current_user.is_authenticated():
        return dict(name=current_user.name, child=db.getavatars(current_user.get_id()).items())

    return None

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', localize=eng, avatars=getavatars())

@app.route('/newlab', methods=['GET', 'POST'])
@login_required
def newlab():
    form = Newlab()
    if form.validate_on_submit():
        db.addlab(form.labname.data)
        return redirect(url_for('index'))
    return render_template('newlab.html', form=form, localize=eng, avatars=getavatars())

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = Signin()
    if form.validate_on_submit():
        if db.adduser(form.username.data, form.password.data, form.laboratory.data):
            return redirect(url_for('login'))
    return render_template('signup.html', form=form, localize=eng)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = db.getuser(form.username.data)
        if user and user['passwd'] == form.password.data:
            login_user(User(user['name'], user['id'], user['active']), remember=True)
            return redirect(url_for('index'))
    return render_template('login.html', form=form, localize=eng)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/about', methods=['GET'])
def about():
    return redirect(url_for('index'))

@app.route('/contacts', methods=['GET'])
def contacts():
    return redirect(url_for('index'))

@app.route('/spectras/<filter>', methods=['GET'])
@login_required
def spectras(filter):
    return redirect(url_for('index'))

@app.route('/user/<name>', methods=['GET'])
@login_required
def user(name):
    return redirect(url_for('index'))
