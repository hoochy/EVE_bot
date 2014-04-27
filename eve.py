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

    def convert_ID_to_human_readable(self, dict_param):

        #превращаем ID в представления
        for key in dict_param.keys():

            if 'AllianceID' in key:
                #проверим, может ID уже заменен на имя
                if dict_param[key].isdigit():
                    dict_param[key] = self.bases['alliance_db'].get_value_by_ID(dict_param[key]).decode()

            if 'solarSystem' in key:
                #проверим, может ID уже заменен на имя
                if dict_param[key].isdigit():
                    dict_param[key] = self.bases['solar_system_db'].get_value_by_ID(dict_param[key]).decode()

            #отдельно отработаем ситуацию когда есть ID чара, установим имя корпорации и альянса из инфо чара
            if 'aggressorID' in key:
                result = self.api.eve.CharacterInfo(characterID = dict_param[key])
                #если корпа не в альянсе, апи не возвращает поле alliance
                try:
                    dict_param['aggressorAllianceID'] = result.alliance
                except:
                    dict_param['aggressorAllianceID'] = 'None'
                dict_param['aggressorCorpID'] = result.corporation
                dict_param['aggressorID'] = result.characterName

            if 'shieldValue' in key:
                dict_param['shieldValue'] = self.string_format(float(dict_param['shieldValue']) * 100) + "%"

            if 'armorValue' in key:
                dict_param['armorValue'] = self.string_format(float(dict_param['armorValue']) * 100) + "%"

            if 'hullValue' in key:
                dict_param['hullValue'] = self.string_format(float(dict_param['hullValue']) * 100) + "%"


        return False

    def decode_notification(self, row_data, typeID):
        #формирование сообщение по типу сообщения из тела нотификации

        #форматы сообщений по типам
        #
        #type= 87                               Атака SBU
        #
        #тело:
        #aggressorAllianceID: 679584932         ID альянса атакующего
        #aggressorCorpID: 1054195408            ID корпы атакующего
        #aggressorID: 512942853                 ID атакующего чара
        #armorValue: 1.0                        Состояние армора *100 %
        #hullValue: 1.0                         Состояние структуры *100%
        #shieldValue: 0.9999299556949086        Состояние шилда *100 %
        #solarSystemID: 30002440                ID солнечной системы

        flag_message_standartitazed = False

        #начинаем разбор тела нотификации
        if typeID != '76' and typeID != '128': #76 сообщение о дефиците топляка в палке, 128 аплик в корпу. там нарушен формат. Его не стандартизируем.
            param_list = row_data.split('\n')
            #print(row_data)
            dict_param = dict([(value.split(':')[0], value.split(': ')[1]) for value in param_list if value and ':' in value])
            flag_message_standartitazed = True

        if flag_message_standartitazed:
            #обработаем наш словарь, заменяя идентификаторы на человечий текст
            self.convert_ID_to_human_readable(dict_param)

            #формируем сообщение
            if typeID == '87':
                template = 'В системе {solarSystemID} атаковано SBU. Атаковал {aggressorID} из корпорации {aggressorCorpID} ( {aggressorAllianceID} ). Состояние SBU:\n' \
                           '    Shield:     {shieldValue}\n' \
                           '    Armor:      {armorValue}\n' \
                           '    Structure:  {hullValue}'
            else:
                template = row_data

            #print(template.format(**dict_param))
            return template.format(**dict_param)

        return row_data

    def get_notification_body_by_ID(self, characterID, notificationID, typeID):

        #возвращает тело нитификации в виде строки по ключу авторизованному в auth, для сообщения с notificationID у чара characterID
        #https://api.eveonline.com/char/NotificationTexts.xml.aspx?keyID=2926885&vCode=YS0gR1goD7dw2IgspU01lr1mjbxGhIjJDRq3jZAq5kiwvCOf0SscBQHQURn8ejT7&characterID=1346573794&IDs=447251281

        #здесь нужно сделать конструктор из долбанного формата ццп в читаемый текст для нужных типов сообщений (атака поса, установка сбу и т.п.)
        result = self.auth.char.NotificationTexts(characterID=characterID, IDs=self.string_format(notificationID))
        message = self.decode_notification(result.notifications[0].data, typeID)
        return message

    def get_notifications(self, filter_type_id=()):

        #выводит все нотификации с телами для всех чаров по ключу авторизованному в auth
        result2 = self.auth.account.Characters()

        news_line = []
        for character in result2.characters:
            NotificatiosID = self.auth.char.Notifications(characterID=character.characterID)
            for RowID in NotificatiosID.notifications:
                typeID = self.string_format(RowID.typeID)
                if len(filter_type_id) != 0:
                    if (typeID not in filter_type_id):
                        continue

                NotificatiosBody = self.get_notification_body_by_ID(characterID = character.characterID, notificationID = RowID.notificationID, typeID = typeID)
                #print (self.string_format(character.name) +  " Date = "+ self.string_format(datetime.datetime.fromtimestamp(RowID.sentDate)) +  "\n" + "[" + NotificatiosBody + "]")
                news_line.append((self.string_format(character.name) +  " Date = " + self.string_format(datetime.datetime.fromtimestamp(RowID.sentDate)) +  "\n" + "[" + NotificatiosBody + "]"))

        return news_line

    def __init__(self, KEYID = '',  VCODE = "", CHARACTERID = ''):

        #создаем экземпляр интерфейса
        self.api = eveapi.EVEAPIConnection()

        #авторизуемся на сервере. необходимы только эти параметры, дополнительные передаются в соответствующие функции.
        self.auth = self.api.auth(keyID=KEYID, vCode=VCODE)

