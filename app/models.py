__author__ = 'stsouko'
from pony.orm import *

db = Database("sqlite", "/tmp/database.sqlite", create_db=True)

class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    passwd = Required(str)
    laboratory = Required("Laboratory")
    avatars = Set("Avatars", reverse="users")
    personalavatar = Optional("Avatars", reverse="user")


class Tasks(db.Entity):
    id = PrimaryKey(int, auto=True)
    time = Required(int)
    key = Required(int)
    status = Required(bool)
    title = Required(str)
    structure = Required(str)
    avatar = Required("Avatars")
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
        if not user:
            lab = Laboratory.get(id=lab)
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
