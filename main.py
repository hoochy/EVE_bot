__author__ = 'hoochy'

ErrorMessage = ''

import configparser, eve, IDConvert, jabber_bot

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

    return True

def ttt():
    print('10 seconds left')

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
    options['bases'] = bases

    #создаем интерфейс в еву
    eve = eve.eve(KEYID = options['KEYID'], VCODE = options['VCODE'], CHARACTERID = options['CHARACTERID'])
    #временно
    eve.bases = bases

    #создаем бота
    xmpp = jabber_bot.EchoBot(options['JID'], options['password'])
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    #передаем боту интерфейс в еву
    xmpp.eve = eve

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block = False)
        xmpp.schedule('testschedule', 10, ttt,repeat = True)
        print("Done")
    else:
        print("Unable to connect.")

    #alliance_list() #создаем базу альянсов
    #get_wallet()
    #solar_system_list()
    #get_notifications()

else:
    print(ErrorMessage)