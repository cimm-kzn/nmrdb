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

rus = dict(logout='Выйти', home='Главная', sub='Иерархия', spectras='Спектры', anon='Аноним', filters='Отсортированные спектры',
           project='NMRdb', contacts='Контакты', login='Логин',
           registration='Регистрация', newlab='Новая лаборатория', fclear='Очиcтить фильтры по пользователям',
           doreg='Новый пользователь', newtask='Новое задание',
           newava='Поменять позицию', newpwd='Новый пароль', setchief='Предоставить спектры', taskcode='номер задания',
           status='Завершен?', user='Имя пользователя',
           time='Время', complete='Работа завершена', notcomplete='В работе', tasktype='образец(тип) задания',
           setcmp='Пометить задание завершенным',
           nextpage='Следущая страница', prevpage='Преведущая страница',
           newavacomment='Необходимо для закрытия доступа к новым спектрам пользователям которыми в прошлом был дан доступ. ',
           toe='Внимание, без регистрации вы не сможете пользоваться данным ресурсом!',
           usersetting='Использовать осторожно!')

loc = dict(logout='Log Out', home='Home', sub='subordinates', spectras='Spectras', anon='Anonymous',
           filters='Filters', project='NMRdb', contacts='Contacts', login='Login',
           registration='Registration', newlab='Change Laboratory', fclear='Clear User filter', doreg='New user?',
           newtask='New Task', newava='Change position', newpwd='New password', setchief='Share spectra',
           taskcode='Task number', status='Complete?', user='User Name', time='Time', complete='Completed',
           notcomplete='In Work', tasktype='Types of task', setcmp='Set as completed', setincmp='Set as incompleted',
           nextpage='Next Page', prevpage='Previous Page',
           setchiefcomments='Share your data (from last laboratory or position change) with somebody (Chief, Head of group, etc)',
           changelabcomments='зачем все это$$$$$',
           newavacomment='зачем менять аву. для отпочковывания^^^^^^',
           toe='условия использования и зачем все это нужно',
           newtaskcomment='task creation instruction',
           banuser='Ban User', changerole='Change Role',
           all='All', cmp='Completed', new='New', profile='Profile',
           taskcodecomment='WHY NEED TASK?', usersetting='Warning! Using carefully')


def localization():
    loc.update(rus)
    return loc
