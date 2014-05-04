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

    textline = '--------------------\nReloading alliance list from EVE API...'

    if not ReplyTo:
        reply = bot.make_message(msg['from'], mbody = textline, mtype='chat')
        reply.send()
    else:
        if 'room' in ReplyTo and 'mtype' in ReplyTo:
            bot.sendMessage(ReplyTo['room'], textline, mtype = ReplyTo['mtype'])
        else:
            return False

    result = bot.eve.api.eve.AllianceList()
    alliance_db = bot.bases['alliance_db']

    for alliance in result.alliances:
        alliance_db.set_value_by_ID(string_format(alliance.allianceID), string_format(alliance.name))
    alliance_db.close_base()

    reply = bot.make_message(msg['from'], mbody = '--------------------\nReloading complete.', mtype='chat')
    reply.send()

    return True