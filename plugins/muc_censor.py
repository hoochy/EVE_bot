__author__ = 'hoochy'
import urllib.request
import urllib.parse
import json

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    #if not bot or not msg:
    #    return False

    #if not ReplyTo:
    #    reply = bot.make_message(msg['from'])
    #else:
    #    reply = bot.make_message(ReplyTo)

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if param_list:
        #есть параметры.
        charname = ' '.join(param_list[0:]).split('@')[0] + '@jb.legionofdeath.ru'
        data = {}
        data['JID'] = charname
        data['secret'] = bot.dash_secretkey
        url_values = urllib.parse.urlencode(data)
        url = 'http://dashboard.legionofdeath.ru/api/jabber/character-info'
        full_url = url + '?' + url_values
        data = json.loads(urllib.request.urlopen(full_url).read().decode())
        if data:
            if 'success' in data:
                if data['success']:
                    correct_name = data['data']['alliance']['ticker'].strip() + ' ' + data['data']['corporation']['ticker'].strip() + ' ' + data['data']['character']['name'].strip()
                else:
                    correct_name = ''
            else:
                correct_name = ''
        else:
            correct_name = ''

    textline = correct_name

    if msg:
        reply = bot.make_message(ReplyTo)
        if not correct_name:
            textline = 'Соответствие не найдено'
        else:
            textline = correct_name

        reply['body'] = textline
        reply['type'] = msg['type']
        reply.send()

    return textline

def help():
    return '--------------------\nPlugin returns character info by JID'

def secret():
    return True