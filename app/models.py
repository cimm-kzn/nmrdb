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
from pony.orm import *
import time
from app.lib.crc8 import CRC8
from random import randint

db = Database("sqlite", "/tmp/database.sqlite", create_db=True)
crc = CRC8()


class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    fullname = Required(str, unique=True)
    name = Required(str, unique=True)
    passwd = Required(str)
    avatars = Set("Avatars", reverse="users")
    personalavatar = Optional("Avatars", reverse="user")
    childavatars = Set("Avatars", reverse="parentuser")
    active = Required(bool)


class Tasks(db.Entity):
    id = PrimaryKey(int, auto=True)
    avatar = Required("Avatars")
    time = Required(int)
    key = Required(str)
    status = Required(bool)
    title = Required(str)
    structure = Required(str)
    spectras = Set("Spectras")
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


sql_debug(True)
db.generate_mapping(create_tables=True)


class NmrDB:
    def __init__(self):
        self.__cost = dict(h1=2, h1_p31=1, p31=5, p31_h1=1, c13=60, c13_h1=60, c13_apt=60, c13_dept=60, f19=1, si29=1,
                           b11=1, noesy=60, hsqc=60, hmbc=60, cosy=60)
        self.__stypekey = {y: x + 1 for x, y in enumerate(sorted(self.__cost))}
        self.__stypeval = {y: x for x, y in self.__stypekey.items()}

    def gettasktypes(self):
        return self.__stypeval

    @db_session
    def adduser(self, fullname, name, passwd, lab):
        user = Users.get(name=name)
        lab = Laboratory.get(id=lab)
        if lab and not user:
            user = Users(fullname=fullname, name=name, passwd=passwd, active=True)
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
    def addlab(self, name):
        lab = Laboratory.get(name=name)
        if not lab:
            Laboratory(name=name)
            return True

        return False

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
    def gettasklist(self, user=0, avatar=0, status=None, page=1, pagesize=50):
        user = Users.get(id=user)
        avatar = Avatars.get(id=avatar)

        if user:
            q = select(x for x in Tasks if x.avatar in user.avatars and (status is None or x.status == status))
        elif avatar:
            q = select(x for x in Tasks if x.avatar == avatar and (status is None or x.status == status))
        else:
            q = select(x for x in Tasks if status is None or x.status == status)

        return [dict(id=x.id, time=x.time, status=x.status, key=x.key) for x in q.order_by(
            Tasks.id.desc()).page(page, pagesize=pagesize)]

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
            user.passwd = passwd
            return True

        return False

    @staticmethod
    def __gettaskkey(key):
        return '%s%d' % (key, crc.calc(key) % 10)

    @db_session
    def addtask(self, user, **kwargs):
        user = Users.get(id=user)
        key = self.__gettaskkey('%04d' % randint(1, 9999))
        if user:
            Tasks(avatar=user.personalavatar, time=int(time.time()), key=key, status=False,
                  title=kwargs.get("title", ''), structure=kwargs.get("structure"),
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
    def getuser(self, name):
        user = Users.get(name=name)
        if user:
            return dict(id=user.id, fullname=user.fullname, name=user.name, passwd=user.passwd, lab=user.personalavatar.laboratory.name,
                        active=user.active)

        return False

    @db_session
    def getuserbyid(self, userid):
        user = Users.get(id=userid)
        if user:
            return dict(id=user.id, fullname=user.fullname, name=user.name, passwd=user.passwd, lab=user.personalavatar.laboratory.name,
                        active=user.active)

        return False

    @db_session
    def gettaskbykey(self, key):
        if key == self.__gettaskkey(key[:4]):
            task = Tasks.get(key=key)
            if task:
                return self.__gettask(task)

        return False

    @db_session
    def gettask(self, task):
        task = Tasks.get(id=task)
        if task:
            return self.__gettask(task)

        return False

    def __gettask(self, task):
        return dict(title=task.title, structure=task.structure, status=task.status,
                    files=[dict(file=x.file, stype=self.__stypeval.get(x.stype, "h1")) for x in task.spectras],
                    h1=task.h1,
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
                    cosy=task.cosy)

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
        for x, y, z in left_join((x.stype, x.task.avatar.laboratory.name, x.task.time) for x in Spectras if x.task.time > stime):
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
