__author__ = 'hoochy'
import datetime

def string_format(value):

    if type(value) == float:
        return "%0.0f" % value
    elif type(value) == int:
        return "%d" % value
    else:
        return "%s" % value

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    global localbot

    if not bot or not msg:
        return False

    localbot = bot

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = '--------------------\nFetching notifications...'
    reply['type'] = msg['type']
    reply.send()

    if param_list:
        #есть параметры. в параметрах мы ожидаем фильтры на типы нотификаций.
        #в параметре должен быть список типов нотификаций
        #заменим человечье представление на евовское по словарю
        translator = notif_types()
        filter = list(translator[type] for type in param_list if type in translator)
        textline = '\n'.join(get_notifications(filter_type_id = filter))

    else:
        textline = '--------------------\nFilter not specified!'

    if not textline:
        textline = '--------------------\nNo notifications'

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = textline
    reply['type'] = msg['type']
    reply.send()

    return True

def notif_types():
    #пока делаем только СБУ
    types = {}
    types['SBU'] = '87'
    types['10'] = '10'
    return types

def help():
    return '--------------------\nPlugin provides list of emergency notifications\nusage:\n\
            get_notifications - list of default notifications\n\
            get_notifications type1 type2 ...- list of notifications of types type1 type2 ...\n\
            \n\
            Types:\n\
            SBU - SBU under attack'

def get_notifications(filter_type_id=()):

    global localbot
    #выводит все нотификации с телами для всех чаров по ключу авторизованному в auth
    result2 = localbot.eve.auth.account.Characters()

    news_line = []
    for character in result2.characters:
        NotificatiosID = localbot.eve.auth.char.Notifications(characterID=character.characterID)
        for RowID in NotificatiosID.notifications:
            typeID = string_format(RowID.typeID)
            if filter_type_id:
                if (typeID not in filter_type_id):
                    continue

            NotificatiosBody = get_notification_body_by_ID(characterID = character.characterID, notificationID = RowID.notificationID, typeID = typeID)
            news_line.append((string_format(character.name) +  " Date = " + string_format(datetime.datetime.fromtimestamp(RowID.sentDate)) +  "\n" + "[" + NotificatiosBody + "]"))

    return news_line

def convert_ID_to_human_readable(dict_param):

    global localbot
    #превращаем ID в представления
    for key in dict_param.keys():

        if 'AllianceID' in key:
            #проверим, может ID уже заменен на имя
            if dict_param[key].isdigit():
                dict_param[key] = localbot.bases['alliance_db'].get_value_by_ID(dict_param[key]).decode()

        if 'solarSystem' in key:
            #проверим, может ID уже заменен на имя
            if dict_param[key].isdigit():
                dict_param[key] = localbot.bases['solar_system_db'].get_value_by_ID(dict_param[key]).decode()

        #отдельно отработаем ситуацию когда есть ID чара, установим имя корпорации и альянса из инфо чара
        if 'aggressorID' in key:
            result = localbot.eve.api.eve.CharacterInfo(characterID = dict_param[key])
            #если корпа не в альянсе, апи не возвращает поле alliance
            try:
                dict_param['aggressorAllianceID'] = result.alliance
            except:
                dict_param['aggressorAllianceID'] = 'None'
            dict_param['aggressorCorpID'] = result.corporation
            dict_param['aggressorID'] = result.characterName

        if 'shieldValue' in key:
            dict_param['shieldValue'] = string_format(float(dict_param['shieldValue']) * 100) + "%"

        if 'armorValue' in key:
            dict_param['armorValue'] = string_format(float(dict_param['armorValue']) * 100) + "%"

        if 'hullValue' in key:
            dict_param['hullValue'] = string_format(float(dict_param['hullValue']) * 100) + "%"

def decode_notification(row_data, typeID):
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
        convert_ID_to_human_readable(dict_param)

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

def get_notification_body_by_ID(characterID, notificationID, typeID):

    global localbot

    #возвращает тело нитификации в виде строки по ключу авторизованному в auth, для сообщения с notificationID у чара characterID

    #здесь нужно сделать конструктор из долбанного формата ццп в читаемый текст для нужных типов сообщений (атака поса, установка сбу и т.п.)
    result = localbot.eve.auth.char.NotificationTexts(characterID=characterID, IDs=string_format(notificationID))
    message = decode_notification(result.notifications[0].data, typeID)
    return message
