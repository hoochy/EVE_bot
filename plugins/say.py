__author__ = 'hoochy'

import collections, sleekxmpp

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if param_list:
        #есть параметры. Первым должно быть имя чата
        room = param_list[0]
        message = ' '.join(param_list[1:])
        toJID = sleekxmpp.JID(room + '@conference.jb.legionofdeath.ru')
        if message:
            reply = bot.make_message(toJID, message, mtype='groupchat')
            reply.send()

        #отчитаемся
        if not ReplyTo:
            reply = bot.make_message(msg['from'])
        else:
            reply = bot.make_message(ReplyTo)

        if message:
            reply['body'] = 'Сообщение отправлено в комнату ' + room
        else:
            reply['body'] = 'Пустые сообщения не отправляю.'
        reply['type'] = msg['type']
        reply.send()

    return True

def help():
    return '--------------------\nPlugin provides message to room \nusage:\n\
            say <room> <message> - say <message> in <room>'

def secret():
    return True

