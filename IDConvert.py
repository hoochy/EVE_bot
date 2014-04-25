__author__ = 'hoochy'

import dbm.dumb
import os

class dbm_base:

    db_file_name = ''
    _db_base = ''
    _flag_opened_for_write = False
    result = False
    message = ''

    def _db_file_exist(self):

        return True

        if self.db_file_name == '':
            return False

        if not os.path.isfile(self.db_file_name):
            f = open(self.db_file_name, 'w')
            f.close()

        return True

    def _base_opened(self, for_write=False):

        if for_write:
            return (self._db_base != '') & (self._flag_opened_for_write)
        return self._db_base != ''

    def _open_base_read(self):

        #проверим, если база уже открыта, закроем, и откроем снова для чтения
        if self._db_base != '':
            self.close_base()

        #проверим файл на существование
        if self._db_file_exist():
            self._db_base = dbm.dumb.open(self.db_file_name, 'r')  # открыть файл базы данных

    def _open_base_write(self):

        #проверим, если база уже открыта, закроем, и откроем снова для записи
        if self._db_base != '':
            self.close_base()

        #проверим файл на существование
        if self._db_file_exist():
            self._db_base = dbm.dumb.open(self.db_file_name, 'r')  # открыть файл базы данных

    def close_base(self):

        if self._db_base != '':
            if self._flag_opened_for_write:
                self._db_base.sync()                    # записать изменения
            self._db_base.close()                       # закрыть базу данных
            self._db_base = ''

    def get_value_by_ID(self, ID):

        if not self._base_opened():
            self._open_base_read()

        if ID in self._db_base:
            self.result = True
            return self._db_base[ID]                    # получить значение по ключу
        else:
            self.result = False
            self.message = 'ID missing'
            return ''

    def set_value_by_ID(self, ID, value):

        if not self._base_opened(for_write=True):
            self._open_base_write()

        self._db_base[ID] = value              # присвоить значение по ключу
