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
from flask import render_template, request, redirect, url_for, make_response
from app.localization import localization
from app import db, app
from app.forms import Registration, Login, Newlab, Newtask, Changelab, Changeava, ChangeChief, Changepwd, Newmsg, \
    Banuser, Gettask
from app.logins import User, admin_required
from flask_login import login_user, login_required, logout_user, current_user
from flask_nav.elements import *
from app.navbar import top_nav, Pagination


loc = localization()
statuscode = dict(all=None, cmp=True, new=False)
taskuserlikekeys = db.gettaskuserlikekeys()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = Newmsg()
    if form.validate_on_submit():
        msg = db.addmessage(title=form.title.data, message=form.message.data)
        if msg:
            return redirect(url_for('index', page=1))

    if page < 1:
        return redirect(url_for('index', page=1))

    msg, pc = db.getmessages(page=page)
    pag = Pagination(page, pc, pagesize=5)
    if page != pag.page:
        return redirect(url_for('index', page=pag.page))

    return render_template('index.html', localize=loc, data=msg, form=form, paginator=pag,
                           user=current_user.get_role() if current_user.is_authenticated else None)


''' TASK
    pages
'''


@app.route('/newtask', methods=['GET', 'POST'])
@login_required
def newtask():
    form = Newtask()
    if form.validate_on_submit():
        tasktypes = dict.fromkeys([db.gettasktypes().get(x, 'h1') for x in form.tasktypes.data], True)
        key = db.addtask(current_user.get_id(), structure=form.structure.data, title=form.taskname.data,
                         solvent=form.solvent.data, **tasktypes)
        if key:
            return render_template('newtaskcode.html', code=key, header=loc['taskcode'],
                                   comments=loc['taskcodecomment'])
    return render_template('newtask.html', form=form, header=loc['newtask'],
                           comments=loc['newtaskcomment'])


@app.route('/spectras/', methods=['GET', 'POST'])
@app.route('/spectras/<sfilter>', methods=['GET', 'POST'])
@login_required
def spectras(sfilter=None):
    form = Gettask()
    if form.validate_on_submit():
        if form.task.data:
            task = db.gettaskbykey(form.task.data)
            if task:
                return redirect(url_for('showtask', task=task['id']))

        return redirect(url_for('spectras', user=form.avatar.data, sfilter=form.filters.data))

    ufilter = request.args.get('user', None)
    sfilter = 'all' if sfilter not in ['all', 'cmp', 'new'] else sfilter
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    if page < 1:
            return redirect(url_for('spectras', sfilter=sfilter, user=ufilter, page=1))

    user = avatar = None
    if ufilter:
        ''' спектры отсортированные по аватарам.
        '''
        access = [x[2] for x in db.getavatars(current_user.get_id())]
        if ufilter in access or current_user.get_role() == 'admin':
            avatar = ufilter
        else:
            user = current_user.get_id()
    elif current_user.get_role() != 'admin':
        ''' все доступные пользователю спектры от всех шар.
        '''
        user = current_user.get_id()

    spectras, sc = db.gettasklist(user=user, avatar=avatar, status=statuscode.get(sfilter), page=page, pagesize=50)
    pag = Pagination(page, sc, pagesize=50)

    return render_template('spectras.html', localize=loc, form=form, data=spectras, paginator=pag, sfilter=sfilter,
                           top_nav=top_nav(sfilter=sfilter, ufilter=ufilter).render(renderer='myrenderer'))


@app.route('/download/<int:task>/<file>', methods=['GET'])
@login_required
def download(task, file):
    if db.chktaskaccess(task, current_user.get_id()):
        resp = make_response()
        resp.headers.extend({'X-Accel-Redirect': '/protected/%s' % file,
                             'Content-Description': 'File Transfer',
                             'Content-Type': 'application/octet-stream'})
        return resp

    return redirect(url_for('index'))


@app.route('/showtask/<int:task>', methods=['GET', 'POST'])
@login_required
def showtask(task):
    task = db.gettask(task, user=None if current_user.get_role() == 'admin' else current_user.get_id())
    if task:
        task['task'] = [(i, taskuserlikekeys.get(i), task['files'].get(i)) for i, j in task['task'].items() if j]
        return render_template('showtask.html', localize=loc, task=task, user=current_user.get_role())
    else:
        return redirect(url_for('spectras', sfilter='all'))


''' COMMON
    pages
'''


@app.route('/contacts', methods=['GET'])
def contacts():
    return render_template('contacts.html')


@app.route('/user/', methods=['GET'])
@app.route('/user/<name>', methods=['GET'])
@login_required
def user(name=None):
    if name:
        user = db.getuser(name=name)
        if user:
            if current_user.get_login() == name:
                user['current'] = True
            return render_template('user.html', localize=loc, user=user)

    return redirect(url_for('user', name=current_user.get_login()))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = Registration()
    if form.validate_on_submit():
        if db.adduser(form.fullname.data, form.username.data, form.password.data, form.laboratory.data):
            return redirect(url_for('login'))
    return render_template('formpage.html', form=form, header=loc['registration'], comments=loc['toe'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = db.getuser(name=form.username.data)
        if user and db.chkpwd(user['id'], form.password.data):
            login_user(User(**user), remember=True)
            return redirect(url_for('index'))
    return render_template('formpage.html', form=form, header=loc['login'], comments='')


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
    return render_template('formpage.html', form=form, header=loc['newava'], comments=loc['newavacomment'])


@app.route('/changelab', methods=['GET', 'POST'])
@login_required
def changelab():
    form = Changelab()
    if form.validate_on_submit():
        if db.changelab(current_user.get_id(), form.laboratory.data):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('formpage.html', form=form, header=loc['newlab'], comments=loc['changelabcomments'])


@app.route('/changepwd', methods=['GET', 'POST'])
@login_required
def changepwd():
    form = Changepwd()
    if form.validate_on_submit():
        if db.changepasswd(current_user.get_id(), form.newpassword.data):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('formpage.html', form=form, header=loc['newpwd'], comments='')


@app.route('/shareava', methods=['GET', 'POST'])
@login_required
def shareava():
    form = ChangeChief()
    if form.validate_on_submit():
        if db.shareava(current_user.get_id(), db.getuser(name=form.name.data)['id']):
            return redirect(url_for('user', name=current_user.get_login()))
    return render_template('formpage.html', form=form, header=loc['setchief'], comments=loc['setchiefcomments'])


''' ADMIN SECTION
    DANGEROUS code
'''


@app.route('/changerole', methods=['GET', 'POST'])
@login_required
@admin_required('admin')
def changerole():
    form = Banuser()
    if form.validate_on_submit():
        users = db.getusersbypartname(form.username.data)
        if users:
            return render_template('changerolelist.html', data=users, localize=loc)
    return render_template('formpage.html', form=form, header=loc['changerole'], comments='')


@app.route('/dochange/<int:user>', methods=['GET'])
@login_required
@admin_required('admin')
def dochange(user):
    role = request.args.get('status')
    if role:
        db.changeuserrole(user, role)
    return redirect(url_for('user', name=current_user.get_login()))


@app.route('/banuser', methods=['GET', 'POST'])
@login_required
@admin_required('admin')
def banuser():
    form = Banuser()
    if form.validate_on_submit():
        users = db.getusersbypartname(form.username.data)
        if users:
            return render_template('banuserlist.html', data=users, localize=loc)
    return render_template('formpage.html', form=form, header=loc['banuser'], comments='')


@app.route('/doban/<int:user>', methods=['GET'])
@login_required
@admin_required('admin')
def doban(user):
    db.banuser(user)
    return redirect(url_for('user', name=current_user.get_login()))


@app.route('/newlab', methods=['GET', 'POST'])
@login_required
@admin_required('admin')
def newlab():
    form = Newlab()
    if form.validate_on_submit():
        db.addlab(form.labname.data)
        return redirect(url_for('user', name=current_user.get_login()))
    return render_template('formpage.html', form=form, header=loc['newlab'], comments='')


@app.route('/setstatus/<int:task>', methods=['GET'])
@login_required
@admin_required('admin')
def setstatus(task):
    status = False if request.args.get('status') else True
    db.settaskstatus(task, status=status)
    return redirect(url_for('showtask', task=task))


@app.route('/addspectra/<int:task>', methods=['GET'])
@login_required
@admin_required('admin')
def addspectra(task):
    stype = request.args.get('stype')
    cname = request.args.get('customname') or '%s.%s.1' % (task, stype)
    db.addspectras(task, cname, stype)
    return redirect(url_for('showtask', task=task))
