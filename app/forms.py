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
from wtforms import StringField, HiddenField, validators, \
    BooleanField, SubmitField, SelectField, PasswordField, ValidationError, SelectMultipleField, TextAreaField
from flask_login import current_user

class CheckExist(object):
    def __init__(self):
        self.message = 'User exist'

    def __call__(self, form, field):
        username = field.data
        if db.getuser(username):
            raise ValidationError(self.message)

class CheckNotExist(object):
    def __init__(self):
        self.message = 'User not found'

    def __call__(self, form, field):
        username = field.data
        if not db.getuser(username):
            raise ValidationError(self.message)

class CheckPwd(object):
    def __init__(self):
        self.message = 'Wrong password'

    def __call__(self, form, field):
        passwd = field.data
        if not db.chkpwd(current_user.get_id(), passwd):
            raise ValidationError(self.message)

class CheckMol(object):
    def __init__(self):
        self.message = 'No structure'

    def __call__(self, form, field):

        if '  0  0  0     0  0            999 V2000' in field.data:
            raise ValidationError(self.message)


class Registration(Form):
    def __init__(self):
        super().__init__()
        self.laboratory.choices = [(x['id'], x['name']) for x in db.getlabslist()]

    fullname = StringField('Full Name', validators=[validators.DataRequired()])
    username = StringField('Login', [validators.DataRequired(), validators.Length(min=4, max=25), CheckExist()])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [validators.DataRequired()])
    laboratory = SelectField('Laboratory', coerce=int)
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit_button = SubmitField('Submit')

class Login(Form):
    username = StringField('Login', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    submit_button = SubmitField('Enter')

class Changelab(Form):
    def __init__(self):
        super().__init__()
        self.laboratory.choices = [(x['id'], x['name']) for x in db.getlabslist()]

    laboratory = SelectField('Laboratory', [validators.DataRequired()], coerce=int)
    password = PasswordField('Password', [validators.DataRequired(), CheckPwd()])
    submit_button = SubmitField('Enter')

class Changepwd(Form):
    password = PasswordField('Password', [validators.DataRequired(), CheckPwd()])
    newpassword = PasswordField('New Password', [validators.DataRequired(),
                                                 validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [validators.DataRequired()])
    submit_button = SubmitField('Enter')

class Changeava(Form):
    password = PasswordField('Password', [validators.DataRequired(), CheckPwd()])
    submit_button = SubmitField('Enter')

class ChangeChief(Form):
    name = StringField('User Name for share', validators=[validators.DataRequired(), CheckNotExist()])
    password = PasswordField('Password', [validators.DataRequired(), CheckPwd()])
    submit_button = SubmitField('Enter')

class Newlab(Form):
    labname = StringField('Laboratory', [validators.DataRequired()])
    submit_button = SubmitField('Enter')

class Banuser(Form):
    username = StringField('User', [validators.DataRequired()])
    submit_button = SubmitField('Enter')

class Newmsg(Form):
    title = StringField('Title', [validators.DataRequired()])
    message = TextAreaField('Message', [validators.DataRequired()])
    submit_button = SubmitField('Enter')

class Newtask(Form):
    def __init__(self):
        super().__init__()
        self.tasktypes.choices = [(x, self.__cost.get(y, y)) for x, y in db.gettasktypes().items()]

    __cost = db.gettaskuserlikekeys()

    taskname = StringField('Title', [validators.DataRequired()])
    tasktypes = SelectMultipleField('Tasks', [validators.DataRequired()], coerce=int)
    structure = HiddenField('structure', [validators.DataRequired(), CheckMol()])
    submit_button = SubmitField('Enter')

