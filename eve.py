__author__ = 'hoochy'

import eveapi
import datetime

class eve:

    def string_format(self, value):

        if type(value) == float:
            return "%0.0f" % value
        elif type(value) == int:
            return "%d" % value
        else:
            return "%s" % value

    def __init__(self, KEYID = '',  VCODE = "", CHARACTERID = ''):

        #создаем экземпляр интерфейса
        self.api = eveapi.EVEAPIConnection()

        #авторизуемся на сервере. необходимы только эти параметры, дополнительные передаются в соответствующие функции.
        self.auth = self.api.auth(keyID=KEYID, vCode=VCODE)

