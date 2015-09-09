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
from math import ceil

__author__ = 'stsouko'
from pony.orm import *
import time
from app.lib.crc8 import CRC8
import datetime
from app import bcrypt, app

if app.config.get("DEBUG"):
    db = Database("sqlite", "../database.sqlite", create_db=True)
else:
    db = Database('mysql', user=app.config.get("DB_USER"), password=app.config.get("DB_PASS"),
                  host=app.config.get("DB_LOC"), database=app.config.get("DB_TABLE"))
crc = CRC8()


class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    fullname = Required(str)
    name = Required(str, unique=True)
    passwd = Required(str)
    avatars = Set("Avatars", reverse="users")
    personalavatar = Optional("Avatars", reverse="user")
    childavatars = Set("Avatars", reverse="parentuser")
    active = Required(bool)
    role = Required(str)


class Tasks(db.Entity):
    id = PrimaryKey(int, auto=True)
    avatar = Required("Avatars")
    time = Required(int)
    key = Required(str)
    status = Required(bool)
    title = Required(str)
    structure = Required(LongStr)
    spectras = Set("Spectras")
    solvent = Required(int)
    h1 = Optional(bool)
    h1_p31 = Optional(bool)
    p31 = Optional(bool)
    p31_h1 = Optional(bool)
    c13 = Optional(bool)
    c13_h1 = Optional(bool)
    c13_apt = Optional(bool)
    c13_dept = Optional(bool)
    f19 = Optional(bool)
    si29 = Optional(bool)
    b11 = Optional(bool)
    noesy = Optional(bool)
    hsqc = Optional(bool)
    hmbc = Optional(bool)
    cosy = Optional(bool)


class Laboratory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    avatars = Set("Avatars")


class Avatars(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Optional(Users, reverse="personalavatar")
    tasks = Set(Tasks)
    users = Set(Users, reverse="avatars")
    parentuser = Required(Users, reverse="childavatars")
    laboratory = Required(Laboratory)


class Spectras(db.Entity):
    id = PrimaryKey(int, auto=True)
    stype = Required(int)
    file = Required(str)
    task = Required(Tasks)


class Blog(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    message = Required(str)
    time = Required(int)


db.generate_mapping(create_tables=True)


class NmrDB:
    def __init__(self):
        self.__cost = dict(h1=2, h1_p31=1, p31=5, p31_h1=1, c13=60, c13_h1=60, c13_apt=60, c13_dept=60, f19=1, si29=1,
                           b11=1, noesy=60, hsqc=60, hmbc=60, cosy=60)
        self.__stypekey = {y: x + 1 for x, y in enumerate(sorted(self.__cost))}
        self.__stypeval = {y: x for x, y in self.__stypekey.items()}
        self.__gettasknumb = self.__tasknumb()
        self.__userlikekey = dict(h1='1H', h1_p31='1H{31P}', p31='31P', p31_h1='31P{1H}', c13='13C', c13_h1='13C{1H}',
                                  c13_apt='13C apt', c13_dept='13C dept135', f19='19F', si29='29Si',
                                  b11='11B', noesy='NOESY', hsqc='HSQC', hmbc='HMBC', cosy='COSY')
        solvent = ['CDCh3', 'D2O', 'D-DMSO']
        self.__solvents = {x: y for x, y in enumerate(solvent)}

    def gettasktypes(self):
        return self.__stypeval

    def getsolvents(self):
        return self.__solvents

    def gettaskuserlikekeys(self):
        return self.__userlikekey

    @db_session
    def adduser(self, fullname, name, passwd, lab, role="common"):
        user = Users.get(name=name)
        lab = Laboratory.get(id=lab)
        if lab and not user:
            passwd = bcrypt.generate_password_hash(passwd)
            user = Users(fullname=fullname, name=name, passwd=passwd, active=True, role=role)
            Avatars(user=user, users=user, laboratory=lab, parentuser=user)
            return True

        return False

    @db_session
    def banuser(self, userid):
        user = Users.get(id=userid)
        if user:
            user.active = False
            return True

        return False

    @db_session
    def changeuserrole(self, userid, role):
        user = Users.get(id=userid)
        if user:
            user.role = role
            return True

        return False

    @db_session
    def addlab(self, name):
        lab = Laboratory.get(name=name)
        if not lab:
            Laboratory(name=name)
            return True

        return False

    @db_session
    def addmessage(self, title, message):
        q = Blog.get(title=title)
        if not q:
            Blog(title=title, message=message, time=int(time.time()))
            return True

        return False

    @db_session
    def getmessages(self, page=1, pagesize=5):
        cc = ceil(count(x for x in Blog) / pagesize)
        if cc and cc >= page:
            q = select(x for x in Blog).order_by(Blog.id.desc()).page(page, pagesize=pagesize)
            return [dict(time=datetime.datetime.fromtimestamp(x.time).strftime('%Y-%m-%d %H:%M:%S'),
                    title=x.title, message=x.message) for x in q], cc

        return [], 1

    @db_session
    def shareava(self, fromuser, touser):
        fromuser = Users.get(id=fromuser)
        touser = Users.get(id=touser)
        if fromuser and touser:
            ava = fromuser.personalavatar
            touser.avatars.add(ava)
            return True

        return False

    @db_session
    def getavatars(self, user):
        user = Users.get(id=user)
        if user:
            return [(x.id, x.parentuser.fullname, x.parentuser.name) for x in user.avatars]

        return False

    @db_session
    def gettasklist(self, user=0, avatar='', status=None, page=1, pagesize=50):
        user = Users.get(id=user)
        avatar = select(x for x in Avatars if x.user.name == avatar).first()  # Avatars.get(id=avatar)

        if user:
            q = select(x for x in Tasks if x.avatar in user.avatars and (status is None or x.status == status))
        elif avatar:
            q = select(x for x in Tasks if x.avatar == avatar and (status is None or x.status == status))
        else:
            q = select(x for x in Tasks if status is None or x.status == status)

        cc = ceil(count(q) / pagesize)
        if cc and cc >= page:
            return [dict(id=x.id, time=datetime.datetime.fromtimestamp(x.time).strftime('%Y-%m-%d %H:%M:%S'),
                    status=x.status, key=x.key, user=x.avatar.parentuser.fullname) for x in
                    q.order_by(Tasks.id.desc()).page(page, pagesize=pagesize)], cc

        return [], 1

    @db_session
    def changeava(self, user):
        user = Users.get(id=user)
        if user:
            lab = user.personalavatar.laboratory
            user.personalavatar = Avatars(user=user, users=user, laboratory=lab, parentuser=user)
            return True

        return False

    @db_session
    def changelab(self, user, lab):
        user = Users.get(id=user)
        lab = Laboratory.get(id=lab)
        if user and lab:
            user.personalavatar = Avatars(user=user, users=user, laboratory=lab, parentuser=user)
            return True

        return False

    @db_session
    def changepasswd(self, user, passwd):
        user = Users.get(id=user)
        if user:
            passwd = bcrypt.generate_password_hash(passwd)
            user.passwd = passwd
            return True

        return False

    @staticmethod
    def __gettaskkey(key):
        return '%s%d' % (key, crc.calc(key) % 10)

    @staticmethod
    def __tasknumb():
        i = int(time.time()) // 1000
        while True:
            i += 1
            yield i % 10000

    @db_session
    def addtask(self, user, **kwargs):
        user = Users.get(id=user)
        key = self.__gettaskkey('%04d' % next(self.__gettasknumb))
        if user:
            Tasks(avatar=user.personalavatar, time=int(time.time()), key=key, status=False,
                  title=kwargs.get("title", ''), structure=kwargs.get("structure"),
                  solvent=kwargs.get('solvent', 0) if kwargs.get('solvent', 0) in self.__solvents else 0,
                  h1=kwargs.get('h1', False),
                  h1_p31=kwargs.get('h1_p31', False),
                  p31=kwargs.get('p31', False),
                  p31_h1=kwargs.get('p31_h1', False),
                  c13=kwargs.get('c13', False),
                  c13_h1=kwargs.get('c13_h1', False),
                  c13_apt=kwargs.get('c13_apt', False),
                  c13_dept=kwargs.get('c13_dept', False),
                  f19=kwargs.get('f19', False),
                  si29=kwargs.get('si29', False),
                  b11=kwargs.get('b11', False),
                  noesy=kwargs.get('noesy', False),
                  hsqc=kwargs.get('hsqc', False),
                  hmbc=kwargs.get('hmbc', False),
                  cosy=kwargs.get('cosy', False))
            return key

        return False

    @db_session
    def getuserbyname(self, name):
        user = Users.get(fullname=name)
        if user:
            return dict(id=user.id, fullname=user.fullname, name=user.name, passwd=user.passwd,
                        lab=user.personalavatar.laboratory.name, active=user.active, role=user.role)

        return False

    @db_session
    def getusersbypartname(self, name):
        q = select((x.id, x.name, x.fullname, x.role) for x in Users if name in x.fullname)
        return [dict(id=x, name=y, fullname=z, role=w) for x, y, z, w in q]

    @db_session
    def getuser(self, name):
        user = Users.get(name=name)
        if user:
            return dict(id=user.id, fullname=user.fullname, name=user.name, passwd=user.passwd,
                        lab=user.personalavatar.laboratory.name, active=user.active, role=user.role)

        return False

    @db_session
    def getuserbyid(self, userid):
        user = Users.get(id=userid)
        if user:
            return dict(id=user.id, fullname=user.fullname, name=user.name, passwd=user.passwd,
                        lab=user.personalavatar.laboratory.name, active=user.active, role=user.role)

        return False

    @db_session
    def chkpwd(self, userid, pwd):
        return bcrypt.check_password_hash(select(x.passwd for x in Users if x.id == userid).first(), pwd)

    @db_session
    def gettaskbykey(self, key):
        if key == self.__gettaskkey(key[:4]):
            task = select(x for x in Tasks if x.key == key).order_by(Tasks.id.desc()).first()
            if task:
                return self.__gettask(task)

        return False

    @db_session
    def gettask(self, task, user=None):
        task = Tasks.get(id=task)

        if task:
            if user:
                user = Users.get(id=user)
                if not (user and task.avatar in user.avatars):
                    return False
            return self.__gettask(task)

        return False

    def __gettask(self, task):
        return dict(title=task.title, structure=task.structure, status=task.status, id=task.id,
                    files={self.__stypeval.get(x.stype, "h1"): x.file for x in task.spectras},
                    solvent=self.__solvents[task.solvent],
                    task=dict(h1=task.h1,
                              h1_p31=task.h1_p31,
                              p31=task.p31,
                              p31_h1=task.p31_h1,
                              c13=task.c13,
                              c13_h1=task.c13_h1,
                              c13_apt=task.c13_apt,
                              c13_dept=task.c13_dept,
                              f19=task.f19,
                              si29=task.si29,
                              b11=task.b11,
                              noesy=task.noesy,
                              hsqc=task.hsqc,
                              hmbc=task.hmbc,
                              cosy=task.cosy))

    @db_session
    def settaskstatus(self, task, status=True):
        task = Tasks.get(id=task)
        if task:
            task.status = status
            return True

        return False

    @db_session
    def getlabslist(self):
        return [dict(id=x.id, name=x.name) for x in Laboratory.select()]

    @db_session
    def addspectras(self, task, name, stype):
        task = Tasks.get(id=task)
        if task:
            Spectras(task=task, stype=self.__stypekey.get(stype, 1), file=name)
            return True

        return False

    @db_session
    def getstatistics(self, stime=0):
        stats = {}
        for x, y, z in left_join(
                (x.stype, x.task.avatar.laboratory.name, x.task.time) for x in Spectras if x.task.time > stime):
            x = self.__stypeval.get(x, 'h1')
            if y in stats:
                if x in stats[y]:
                    stats[y][x] += 1
                else:
                    stats[y][x] = 1
            else:
                stats[y] = {x: 1}
        for i, j in stats.items():
            stats[i]['time'] = sum([self.__cost.get(x) * y for x, y in j.items()])
        return stats
