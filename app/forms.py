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
from app import db
from flask_wtf import Form
from wtforms import StringField, HiddenField, RadioField, validators, \
    BooleanField, SubmitField, SelectField, PasswordField

class Signin(Form):
    fullname = StringField('Full Name', validators=[validators.DataRequired()])
    username = StringField('Login', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [validators.DataRequired(),
                                              validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [validators.DataRequired()])
    laboratory = SelectField('Laboratory', coerce=int, choices=[(x['id'], x['name']) for x in db.getlabslist()])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit_button = SubmitField('Submit')

class Login(Form):
    username = StringField('Login', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    submit_button = SubmitField('Enter')

class Newlab(Form):
    labname = StringField('Laboratory', [validators.DataRequired()])
    submit_button = SubmitField('Enter')
