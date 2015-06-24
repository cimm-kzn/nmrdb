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

rus = dict(logout='Выйти')

loc = dict(logout='Log Out', home='Home', sub='subordinates', spectras='Spectras', anon='Anonymous',
           filters='Filters', project='NMRdb', about='About', contacts='Contacts', login='Login',
           registration='Registration', newlab='New Laboratory', fclear='Clear User filter', doreg='New user?',
           newtask='New Task', newava='Change position', newpwd='New password', setchief='Share spectra',
           taskcode='Task number', status='Complete?', user='User Name', time='Time')

def localization():
    loc.update(rus)
    return loc
