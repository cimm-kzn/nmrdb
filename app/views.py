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
from functools import wraps

__author__ = 'stsouko'
from flask import render_template, request, redirect, url_for
from app import app
from app.localization import localization
from app import db
from app.forms import Registration, Login, Newlab, Newtask, Changelab, Changeava, ChangeChief, Changepwd
from app.logins import User
from flask_login import login_user, login_required, logout_user, current_user


loc = localization()
statuscode = dict(all=None, cmp=True, new=False)
taskuserlikekeys = db.gettaskuserlikekeys()


def admin_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if role and current_user.get_role() != role:
                return redirect(url_for('index'))
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


def getavatars(sfilter='all', ufilter=None):
    if current_user.is_authenticated():
        return dict(name=current_user.name, child=db.getavatars(current_user.get_id()),
                    ufilter=ufilter, sfilter=sfilter, login=current_user.get_login())

    return None


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', localize=loc, data=getavatars())


''' TASK
    pages
'''


@app.route('/newtask', methods=['GET', 'POST'])
@login_required
def newtask():
    form = Newtask()
    if form.validate_on_submit():
        tasktypes = dict.fromkeys([db.gettasktypes().get(x, 'h1') for x in form.tasktypes.data], True)
        key = db.addtask(current_user.get_id(), structure=form.structure.data, title=form.taskname.data, **tasktypes)
        if key:
            return redirect(url_for('newtaskcode', code=key))
    return render_template('newtask.html', form=form, localize=loc, data=getavatars())


@app.route('/newtaskcode/<code>', methods=['GET'])
@login_required
def newtaskcode(code):
    return render_template('newtaskcode.html', code=code, localize=loc, data=getavatars())


@app.route('/spectras/<sfilter>', methods=['GET'])
@login_required
@app.cache.cached(timeout=20)
def spectras(sfilter):
    sfilter = 'all' if sfilter not in ['all', 'cmp', 'new'] else sfilter
    ufilter = request.args.get('user', None)
    page = int(request.args.get('page', 1))
    if ufilter:
        ''' спектры отсортированные по аватарам.
        '''
        user = 0
        access = [x[2] for x in db.getavatars(current_user.get_id())]
        avatar = ufilter if ufilter in access or current_user.get_role() == 'admin' else ''
    elif current_user.get_role() == 'admin':
        ''' админский доступ ко все спектрам. нужно только для добавления в обработку по сути.
        '''
        user = 0
        avatar = ''
    else:
        ''' все доступные пользователю спектры от всех шар.
        '''
        user = current_user.get_id()
        avatar = ''

    spectras = db.gettasklist(user=user, avatar=avatar, status=statuscode.get(sfilter), page=page, pagesize=50)
    return render_template('spectras.html', localize=loc,
                           data=getavatars(sfilter=sfilter, ufilter=ufilter), slist=spectras)


@app.route('/showtask/<int:task>', methods=['GET', 'POST'])
@login_required
@app.cache.cached(timeout=20)
def showtask(task):
    task = db.gettask(task, user=None if current_user.get_role() == 'admin' else current_user.get_id())
    if task:
        task['task'] = [taskuserlikekeys.get(i) for i, j in task['task'].items() if j]
        return render_template('showtask.html', localize=loc, data=getavatars(), task=task,
                               user=dict(role=current_user.get_role()))
    else:
        return redirect(url_for('spectras', sfilter='all'))


''' COMMON
    pages
'''


@app.route('/about', methods=['GET'])
def about():
    return redirect(url_for('index'))


@app.route('/contacts', methods=['GET'])
def contacts():
    return redirect(url_for('index'))


@app.route('/user/', methods=['GET'])
@app.route('/user/<name>', methods=['GET'])
@login_required
def user(name=None):
    if name:
        user = db.getuser(name)
        if user:
            if current_user.get_login() == name:
                user['current'] = True
            return render_template('user.html', localize=loc, data=getavatars(), user=user)

    return redirect(url_for('user', name=current_user.get_login()))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = Registration()
    if form.validate_on_submit():
        if db.adduser(form.fullname.data, form.username.data, form.password.data, form.laboratory.data):
            return redirect(url_for('login'))
    return render_template('registration.html', form=form, localize=loc)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = db.getuser(form.username.data)
        if user and db.chkpwd(user['id'], form.password.data):
            login_user(User(**user), remember=True)
            return redirect(url_for('index'))
    return render_template('login.html', form=form, localize=loc)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/changepos', methods=['GET', 'POST'])
@login_required
def changeava():
    form = Changeava()
    if form.validate_on_submit():
        if db.changeava(current_user.get_id()):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('newava.html', form=form, localize=loc, data=getavatars())


@app.route('/changelab', methods=['GET', 'POST'])
@login_required
def changelab():
    form = Changelab()
    if form.validate_on_submit():
        if db.changelab(current_user.get_id(), form.laboratory.data):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('changelab.html', form=form, localize=loc, data=getavatars())


@app.route('/changepwd', methods=['GET', 'POST'])
@login_required
def changepwd():
    form = Changepwd()
    if form.validate_on_submit():
        if db.changepasswd(current_user.get_id(), form.newpassword.data):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('newpwd.html', form=form, localize=loc, data=getavatars())


@app.route('/shareava', methods=['GET', 'POST'])
@login_required
def shareava():
    form = ChangeChief()
    if form.validate_on_submit():
        if db.shareava(current_user.get_id(), db.getuser(form.name.data)['id']):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('setchief.html', form=form, localize=loc, data=getavatars())


''' ADMIN SECTION
    DANGEROUS code
'''


@app.route('/newlab', methods=['GET', 'POST'])
@login_required
@admin_required('admin')
def newlab():
    form = Newlab()
    if form.validate_on_submit():
        db.addlab(form.labname.data)
        return redirect(url_for('user', name=current_user.get_login()))
    return render_template('newlab.html', form=form, localize=loc, data=getavatars())


@app.route('/setstatus/<int:task>', methods=['GET'])
@login_required
@admin_required('admin')
def setstatus(task):
    db.settaskstatus(task)
    return redirect(url_for('showtask', task=task))
