__author__ = 'hoochy'

def string_format(value):

    if type(value) == float:
        return "%0.0f" % value
    elif type(value) == int:
        return "%d" % value
    else:
        return "%s" % value

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = '--------------------\nReloading solar system list from EVE API...'
    reply['type'] = msg['type']
    reply.send()

    result = bot.eve.api.map.Sovereignty()
    solar_system_db = bot.bases['solar_system_db']

    for system in result.solarSystems:
        solar_system_db.set_value_by_ID(string_format(system.solarSystemID), string_format(system.solarSystemName))
    solar_system_db.close_base()

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = '--------------------\nReloading complete.'
    reply['type'] = msg['type']
    reply.send()

    return True

def secret():
    return True