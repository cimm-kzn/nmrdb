__author__ = 'stsouko'
from pony.orm import *
import time
from .lib.crc8 import crc8
from random import randint

db = Database("sqlite", "/tmp/database.sqlite", create_db=True)
crc = crc8()


class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    passwd = Required(str)
    laboratory = Required("Laboratory")
    avatars = Set("Avatars", reverse="users")
    personalavatar = Optional("Avatars", reverse="user")


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
    users = Set(Users)


class Avatars(db.Entity):
    id = PrimaryKey(int, auto=True)
    tasks = Set(Tasks)
    users = Set(Users, reverse="avatars")
    user = Optional(Users, reverse="personalavatar")


class Spectras(db.Entity):
    id = PrimaryKey(int, auto=True)
    stype = Required(int)
    file = Required(str)
    task = Required(Tasks)


sql_debug(True)
db.generate_mapping(create_tables=True)


class NmrDB:
    @db_session
    def adduser(self, name, passwd, lab):
        user = Users.get(name=name)
        lab = Laboratory.get(id=lab)
        if lab and not user:
            user = Users(name=name, passwd=passwd, laboratory=lab)
            Avatars(user=user, users=user)
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
    def addava(self, fromuser, touser):
        fromuser = Users.get(id=fromuser)
        touser = Users.get(id=touser)
        if fromuser and touser:
            ava = fromuser.personalavatar
            touser.avatars.add(ava)
            return True

        return False

    @db_session
    def changeava(self, user):
        user = Users.get(id=user)
        if user:
            user.personalavatar = Avatars(user=user, users=user)
            return True

        return False

    @db_session
    def changepasswd(self, user, passwd):
        user = Users.get(id=user)
        if user:
            user.passwd = passwd
            return True

        return False

    @db_session
    def changelab(self, user, lab):
        user = Users.get(id=user)
        lab = Laboratory.get(id=lab)
        if user and lab:
            user.laboratory = lab
            return True

        return False

    @db_session
    def addtask(self, user, **kwargs):
        user = Users.get(id=user)
        key = '%04d' % randint(1, 9999)
        key = '%s%03d' % (key, crc.calc(key))
        if user:
            Tasks(avatar=user.personalavatar, time=time.time(), key=key, status=False,
                  title=kwargs.get("title", ''), structure=kwargs.get("structure"),
                  h1=kwargs.get('1h', False))
            return key

        return False

    @db_session
    def getuser(self, name):
        user = Users.get(name=name)
        if user:
            return dict(id=user.id, name=user.name, passwd=user.passwd)

        return False

    @db_session
    def gettaskbykey(self, key):
        if key == '%s%03d' % (key[:4], crc.calc(key[:4])):
            task = Tasks.get(key=key)
            if task:
                return dict(title=task.title, structure=task.structure)

        return False

    @db_session
    def gettask(self, task):
        task = Tasks.get(id=task)
        if task:
            return dict(title=task.title, structure=task.structure, status=task.status,
                        files=[dict(file=x.file, stype=x.stype) for x in task.spectras])

        return False

    @db_session
    def settaskstatus(self, task, status=True):
        task = Tasks.get(id=task)
        if task:
            task.status = status
            return True

        return False

    @db_session
    def gettasklist(self, user=None, status=None):
        if user is not None:
            user = Users.get(id=user)

        return [dict(id=x.id, time=x.time, status=x.status, key=x.key) for x in select(
            x for x in Tasks if (status is None or x.status == status) and (user is None or x.avatar in user.avatars))]

    @db_session
    def getlabslist(self):
        return [dict(id=x.id, name=x.name) for x in Laboratory.select()]
