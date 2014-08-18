__author__ = 'hoochy'

import collections

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if param_list:
        #есть параметры. Первым должно быть имя группы для редактирования
        group = param_list[0]

        reply = bot.make_message(msg['from'], msubject = 'Edit group')
        form = reply['form']

        fields = collections.OrderedDict()

        #получим список групп
        group_db = bot.bases['group_db']
        group_list = group_db.get_value_by_ID(group).decode()
        if not group_list:
            group_list = ''

        fields['Group'] = {'type': 'text-single',
                        'label': 'Group',
                        'value': group}

        fields['GroupContent'] = {'type': 'text-multi',
                        'label': '; separated list',
                        'value': group_list}

        form['fields'] = fields
        form['title'] = 'Group management'

        reply.send()

    return True

def help():
    return '--------------------\nPlugin provides management for groups\nusage:\n\
            mg <groupname>- open form\n\'' \
           'group with empty list will be deleted'