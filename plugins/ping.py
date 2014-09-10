__author__ = 'hoochy'

from sleekxmpp.exceptions import IqError
import sleekxmpp

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if param_list:
        #есть параметры. нас интересует только первый
        name = param_list[0] + '@jb.legionofdeath.ru'
        try:
            result = bot.plugin['xep_0012'].get_last_activity(name)
            seconds = int(result['last_activity']['seconds'])
            if seconds == 0:
                textline = 'Пользователь ' + name + ' сейчас онлайн.'
                JID = sleekxmpp.JID(name)
                notify = bot.make_message(JID)
                notify['body'] = 'Тебя разыскивает ' + bot.JID_to_realJID(msg).bare
                notify['type'] = 'Normal'
                notify.send()
            else:
                textline = 'Пользователь ' + name + ' был онлайн ' + bot.one_day_delta_to_str(seconds) + '.'
        except IqError as err:
            textline = 'Ошибка при получении данных о ' + name
        except:
            pass

    else:
        textline = 'Не задано имя'

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = textline
    reply['type'] = msg['type']
    reply.send()

    return True

def help():
    return '--------------------\nPlugin shows is user online or not\nusage:\n\
            ping <name> - ping user named <name>'