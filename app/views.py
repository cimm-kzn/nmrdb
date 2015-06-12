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
from flask import render_template, request, session, flash, redirect, url_for
from app import app
from app.localization import eng, rus

from flask_wtf import Form, RecaptchaField
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField
from wtforms.validators import DataRequired


class Signin(Form):
    name = StringField('User Name', description='enter your name.', validators=[DataRequired()])
    login = StringField('Login', description='enter login name.', validators=[DataRequired()])
    hidden_field = HiddenField('You cannot see this', description='Nope')
    submit_button = SubmitField('Submit Form')
    #recaptcha = RecaptchaField('A sample recaptcha field')
    #checkbox_field = BooleanField('This is a checkbox', description='Checkboxes can be tricky.')

    #def validate_hidden_field(form, field):
    #    raise ValidationError('Always wrong')



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = Signin()
    form.validate_on_submit()  # to get error messages to the browser
    return render_template('signup.html', form=form, localize=eng)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['user'] = app.config['USERNAME']
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error, title='Login')


@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

