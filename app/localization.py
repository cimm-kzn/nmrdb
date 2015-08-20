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

rus = dict(logout='Выйти',home='Главная', sub='иерархия', spectras='Спектры', anon='Аноним', filters='фильтры', project='NMRdb', contacts='контакты', login='Логин',
           registration='Регистрация', newlab='Новая лаборатория', fclear='очиcтить фильтры по пользователям', doreg='Новый пользователь', newtask='Новое задание',
            newava='Поменять позицию', newpwd='Новый пароль', setchief='поделиться спектром', taskcode='номер задания', status='Завершон?', user='Имя пользователя',
           time='время', complete='работа завершена', notcomplete='В работе', tasktype='образец(тип) задания', setcmp='установить завершение работы',
            nextpage='следущая страница', prevpage='преведущая страница', newavacomment='При переходе из одной лаборатории в другую следует зарегистрироваться, как новому пользователю.'
            toe='Внимание, без регистрации вы не сможете пользоваться данным ресурсом!')


loc = dict(logout='Log Out', home='Home', sub='subordinates', spectras='Spectras', anon='Anonymous',
           filters='Filters', project='NMRdb', contacts='Contacts', login='Login',
           registration='Registration', newlab='New Laboratory', fclear='Clear User filter', doreg='New user?',
           newtask='New Task', newava='Change position', newpwd='New password', setchief='Share spectra',
           taskcode='Task number', status='Complete?', user='User Name', time='Time', complete='Completed',
           notcomplete='In Work', tasktype='Types of task', setcmp='Set as completed', setincmp='Set as incompleted',
           nextpage='Next Page', prevpage='Previous Page',
           setchiefcomments='зачем все это#####',
           changelabcomments='зачем все это$$$$$',
           newavacomment='зачем менять аву. для отпочковывания^^^^^^',
           toe='условия использования и зачем все это нужно')

def localization():
    loc.update(rus)
    return loc
