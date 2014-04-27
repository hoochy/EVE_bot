__author__ = 'hoochy'

def string_format(value):

    if type(value) == float:
        return "%0.0f" % value
    elif type(value) == int:
        return "%d" % value
    else:
        return "%s" % value

def exec(bot = False, msg = None, ReplyTo = None, auth = None):

    if not bot or not msg:
        return False

    reply = bot.make_message(msg['from'], mbody = '--------------------\nReloading solar system list from EVE API...', mtype='chat')
    reply.send()

    result = bot.eve.api.map.Sovereignty()
    solar_system_db = bot.bases['solar_system_d']

    for system in result.solarSystems:
        solar_system_db.set_value_by_ID(string_format(system.solarSystemID), string_format(system.solarSystemName))
    solar_system_db.close_base()

    reply = bot.make_message(msg['from'], mbody = '--------------------\nReloading complete.', mtype='chat')
    reply.send()

    return True