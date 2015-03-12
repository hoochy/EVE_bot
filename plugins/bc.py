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
        #есть параметры. Первым должно быть имя группы, все остальное текст сообщения
        group = param_list[0]
        #получим список групп
        group_db = bot.bases['group_db']
        item = group_db.get_value_by_ID(group).decode()

        bc_from = bot.JID_to_realJID(msg).bare
        bcmessage = ' '.join(param_list[1:])
        if item:
            items = item.split(';')
            for item in items:
                    toJID = sleekxmpp.JID(jid=item + '@broadcast.jb.legionofdeath.ru')
                    reply = bot.make_message(toJID, 'Broadcast from '+ bc_from + ' to ' + group + '\n' + bcmessage, mtype='normal')
                    reply.send()

            #отчитаемся
            if not ReplyTo:
                reply = bot.make_message(msg['from'])
            else:
                reply = bot.make_message(ReplyTo)
            reply['body'] = 'Сделан бродкаст группе ' + group
            reply['type'] = msg['type']
            reply.send()
        else:
            if not ReplyTo:
                reply = bot.make_message(msg['from'])
            else:
                reply = bot.make_message(ReplyTo)
            reply['body'] = "Group <" + group + "> not found"
            reply['type'] = msg['type']
            reply.send()

    else:
        #параметров не передали, откроем форму
        reply = bot.make_message(msg['from'], msubject = 'Broadcast')
        form = reply['form']

        fields = collections.OrderedDict()

        #получим список групп
        group_db = bot.bases['group_db']
        items = group_db.get_list()

        options = []
        for item in items:
            options.append({'label': item.decode(),'value': group_db.get_value_by_ID(item).decode()})
            #print(item + group_db.get_value_by_ID(item))
        fields['Group'] = {'type': 'list-single',
                        'label': 'Group',
                        'options': options}

                        #'options': [{'label': 'test',
                        #             'value': 'test'},
                        #            {'label': 'Fleet Commanders',
                        #             'value': 'Fleet Commanders'}]}

        fields['Broadcast'] = {'type': 'text-multi',
                        'label': 'Broadcast',
                        'value': 'New broadcast text\nhere'}

        form['fields'] = fields
        form['title'] = 'New broadcast'

        reply.send()

    return True

def help():
    return '--------------------\nPlugin provides broadcast messages for groups\nusage:\n\
            bc - open form\n\
            bc <group> <message> - broadcast <message> to <group>'

