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

    result = bot.eve.api.server.ServerStatus()
    if result.serverOpen == 'True':
        textline = '\nСервер онлайн.\nИгроков онлайн: %s' % result.onlinePlayers
    else:
        textline = 'Сервер офлайн.'

    reply['body'] = textline
    reply['type'] = msg['type']
    reply.send()

    return True

def help():
    return '--------------------\nPlugin shows status of EVE server'

def secret():
    return False