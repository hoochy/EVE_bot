__author__ = 'hoochy'

import collections, sleekxmpp

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    #получим список групп
    group_db = bot.bases['group_db']
    items = group_db.get_list()

    reply['body'] = ', '.join(item.decode() for item in items)
    reply['type'] = msg['type']
    reply.send()

    return True

def help():
    return '--------------------\nPlugin provides a list of groups to broadcast plugin\nusage:\n\
            bc_list - print list of groups'
