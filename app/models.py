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
        else:
            return False

    @db_session
    def addlab(self, name):
        lab = Laboratory.get(name=name)
        if not lab:
            Laboratory(name=name)
            return True
        else:
            return False

    @db_session
    def addava(self, fromuser, touser):
        fromuser = Users.get(id=fromuser)
        touser = Users.get(id=touser)
        if fromuser and touser:
            ava = fromuser.personalavatar
            touser.avatars.add(ava)
            return True
        else:
            return False

    @db_session
    def getnewava(self, user):
        user = Users.get(id=user)
        if user:
            user.personalavatar = Avatars(user=user, users=user)
            return True
        else:
            return False

    @db_session
    def changepasswd(self, user, passwd):
        user = Users.get(id=user)
        if user:
            user.passwd = passwd

    @db_session
    def changelab(self, user, lab):
        user = Users.get(id=user)
        lab = Laboratory.get(id=lab)
        if user and lab:
            user.laboratory = lab

    @db_session
    def addtask(self, user, **kwargs):
        user = Users.get(id=user)
        key = '%04d' % randint(1, 9999)
        key = '%s%03d' % (key, crc.calc(key))
        if user:
            Tasks(avatar=user.personalavatar, time=time.time(), key=key, status=False)
            return key
        else:
            return False

    @db_session
    def f(self, user):
        pass