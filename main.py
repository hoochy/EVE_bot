__author__ = 'hoochy'

ErrorMessage = ''

import configparser, eve, IDConvert, jabber_bot, os

def ReadConfig(options):
    global ErrorMessage
    #функция чтения настроек
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not config.has_section('Jabber'):
        ErrorMessage = 'Section "Jabber" not found!'
        return False

    if not config.has_section('EVE'):
        ErrorMessage = 'Section "EVE" not found!'
        return False

    if not config.has_section('DB'):
        ErrorMessage = 'Section "DB" not found!'
        return False

    if not config.has_option('Jabber','JID'):
        ErrorMessage = 'Option "JID" not found in section "Jabber"!'
        return False
    options['JID'] = config.get('Jabber','JID')

    if not config.has_option('Jabber','password'):
        ErrorMessage = 'Option "password" not found in section "Jabber"!'
        return False
    options['password'] = config.get('Jabber','password')

    if not config.has_option('EVE','KEYID'):
        ErrorMessage = 'Option "KEYID" not found in section "EVE"!'
        return False
    options['KEYID'] = config.get('EVE','KEYID')

    if not config.has_option('EVE','VCODE'):
        ErrorMessage = 'Option "VCODE" not found in section "EVE"!'
        return False
    options['VCODE'] = config.get('EVE','VCODE')

    if not config.has_option('EVE','CHARACTERID'):
        ErrorMessage = 'Option "CHARACTERID" not found in section "EVE"!'
        return False
    options['CHARACTERID'] = config.get('EVE','CHARACTERID')

    if not config.has_option('DB','DB_ALLIANCE_FILENAME'):
        ErrorMessage = 'Option "DB_ALLIANCE_FILENAME" not found in section "DB"!'
        return False
    options['DB_ALLIANCE_FILENAME'] = config.get('DB','DB_ALLIANCE_FILENAME')

    if not config.has_option('DB','DB_SOLAR_SYSTEM_FILENAME'):
        ErrorMessage = 'Option "DB_SOLAR_SYSTEM_FILENAME" not found in section "DB"!'
        return False
    options['DB_SOLAR_SYSTEM_FILENAME'] = config.get('DB','DB_SOLAR_SYSTEM_FILENAME')

    if not config.has_option('DB','DB_GROUPS'):
        ErrorMessage = 'Option "DB_GROUPS" not found in section "DB"!'
        return False
    options['DB_GROUPS'] = config.get('DB','DB_GROUPS')

    if config.has_option('MUC','mucnick') and config.has_option('MUC','rooms'):
        options['mucnick'] = config.get('MUC','mucnick')
        options['rooms'] = config.get('MUC','rooms').split(',')
    else:
        options['mucnick'] = 'death'
        options['rooms'] = ()

    if config.has_option('MUC','censor'):
        options['censor'] = config.get('MUC','censor')
    else:
        options['censor'] = 'False'

    if config.has_option('DASH_API','secretkey'):
        options['secretkey'] = config.get('DASH_API','secretkey')
    else:
        options['secretkey'] = 'nokey'

    if config.has_option('MUC','botroom'):
        options['botroom'] = config.get('MUC','botroom')
    else:
        options['botroom'] = False

    i = 1
    MULTIEVE = []
    while True:
        if not config.has_section('MULTIEVE%s' % i):
            break

        SINGLEEVE = {}
        if not config.has_option('MULTIEVE%s' % i,'KEYID'):
            ErrorMessage = 'Option "KEYID" not found in section "MULTIEVE"%s!' % i
            return False
        SINGLEEVE['KEYID'] = config.get('MULTIEVE%s' % i,'KEYID')

        if not config.has_option('MULTIEVE%s' % i,'VCODE'):
            ErrorMessage = 'Option "VCODE" not found in section "MULTIEVE"%s!' % i
            return False
        SINGLEEVE['VCODE'] = config.get('MULTIEVE%s' % i,'VCODE')

        if not config.has_option('MULTIEVE%s' % i,'CHARACTERID'):
            ErrorMessage = 'Option "CHARACTERID" not found in section "MULTIEVE"%s!' % i
            return False
        SINGLEEVE['CHARACTERID'] = config.get('MULTIEVE%s' % i,'CHARACTERID')
        SINGLEEVE['eve'] = ''
        MULTIEVE.append(SINGLEEVE)
        options['MULTIEVE'] = MULTIEVE
        i = i + 1

    return True

def loadPlugins():

    commands = []
    secret_commands = []
    #Перебираем все файлы из папки plugins
    for fname in os.listdir('plugins/'):
        #Если файл заканчивается на '.py'
        if fname.endswith('.py'):
            #Обрезаем последние 3 буквы
            plugin_name = fname[:-3]
            #Если имя файла не '__init__'
            if plugin_name != '__init__':
                #Загружаем плагин в переменную
                plugins = __import__('plugins.'+plugin_name)
                #Достаем плагин с переменной
                commands.append(plugin_name)
                #проверим плагин на наличие признака секретность (доступен не всем)
                try:
                    module = getattr(plugins,plugin_name)
                    if module.secret():
                        secret_commands.append(plugin_name)
                except:
                    pass


    #Возвращаем ассоциативный словарь
    return {'storage':plugins, 'commands':commands, 'secret_commands':secret_commands}

options = {}

if ReadConfig(options):
    #прочитали конфигурацию в словарь
    #создаем базы объектов и добавляем в options
    bases = {}
    #альянсы
    alliance_db = IDConvert.dbm_base() # создаем экземпляр базы альянсов
    alliance_db.db_file_name = options['DB_ALLIANCE_FILENAME']
    bases['alliance_db'] = alliance_db

    #солнечные системы
    solar_system_db = IDConvert.dbm_base() # создаем экземпляр базы солнечных систем
    solar_system_db.db_file_name = options['DB_SOLAR_SYSTEM_FILENAME']
    bases['solar_system_db'] = solar_system_db

    #группы для броадкаста
    group_db = IDConvert.dbm_base() # создаем экземпляр базы групп броадкастов
    group_db.db_file_name = options['DB_GROUPS']
    bases['group_db'] = group_db

    #создаем интерфейс в еву
    evebot = eve.eve(KEYID = options['KEYID'], VCODE = options['VCODE'], CHARACTERID = options['CHARACTERID'])
    #временно
    evebot.bases = bases

    #создадим интерфейсы в еву по коллекции ключей из настроек
    for item in options['MULTIEVE']:
        item['eve'] = eve.eve(KEYID = item['KEYID'], VCODE = item['VCODE'], CHARACTERID = item['CHARACTERID'])


    #создаем бота
    xmpp = jabber_bot.EchoBot(options['JID'], options['password'])
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.register_plugin('xep_0045') # XMPP MUC
    xmpp.register_plugin('xep_0012') # last activity
    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    #передаем боту конфиг
    xmpp.options = options
    #передаем боту интерфейс в еву
    xmpp.eve = evebot
    #передаем боту список аккаунтов еве
    xmpp.multieve = options['MULTIEVE']
    #передаем боту базы
    xmpp.bases = bases
    #передаем список плагинов
    xmpp.plugins = loadPlugins()
    #команта доклада ботов
    xmpp.botroom = options['botroom']

    #передаем боту список комнат для присутсвия и имя в конфах
    xmpp.mucnick = options['mucnick']
    xmpp.rooms = options['rooms']

    #режим контроля ников
    if options['censor'] == 'True':
        xmpp.censor = True
    else:
        xmpp.censor = False

    #передаем боту секретный ключ
    xmpp.dash_secretkey = options['secretkey']
    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...

        #подключаемся к конфам
        #xmpp.plugin['xep_0045'].joinMUC('legionofxxdeathxx@conference.jb.legionofdeath.ru', xmpp.nick)
        #xmpp.plugin['xep_0045'].joinMUC('veryindustrialcorp@conference.jb.legionofdeath.ru', xmpp.nick)
        for room in xmpp.rooms:
            xmpp.plugin['xep_0045'].joinMUC(room + '@conference.jb.legionofdeath.ru', xmpp.mucnick)
            #обработчик пресенсе в комнатах, для сопоставления с реальным джидом
            xmpp.add_event_handler("muc::%s@conference.jb.legionofdeath.ru::presence" % room,
                           xmpp.muc_presense)
            #обработчик захода пользователя в комнату
            xmpp.add_event_handler("muc::%s@conference.jb.legionofdeath.ru::got_online" % room,
                           xmpp.muc_online)
        #комната для докладов бота
        if options['botroom']:
            xmpp.plugin['xep_0045'].joinMUC(options['botroom'] + '@conference.jb.legionofdeath.ru', xmpp.mucnick)

        xmpp.process(block = False)
        print("Bot started")
    else:
        print("Unable to connect.")

else:
    print(ErrorMessage)