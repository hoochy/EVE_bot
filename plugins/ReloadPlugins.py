__author__ = 'hoochy'
import os

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    reply = bot.make_message(msg['from'], mbody = '--------------------\nReloading plugins...', mtype='chat')
    reply.send()
    #сохраним старый список команд
    old_list = list(bot.plugins['commands'])

    commands = []
    secret_commands = []

    #Перебираем все файлы из папки plugins
    for fname in os.listdir('plugins/'):
        #Если файл заканчивается на '.py'
        if fname.endswith('.py'):
            #Обрезаем последние 3 буквы
            plugin_name = fname[:-3]
            #Если имя файла не '__init__'
            if plugin_name != '__init__':
                #Загружаем плагин в переменную
                plugins = __import__('plugins.'+plugin_name)
                #Достаем плагин с переменной
                commands.append(plugin_name)
                #проверим плагин на наличие признака секретность (доступен не всем)
                try:
                    module = getattr(plugins,plugin_name)
                    if module.secret():
                        secret_commands.append(plugin_name)
                except:
                    pass

    bot.plugins = {'storage':plugins, 'commands':commands}

    miss_list = list(name for name in old_list if name not in commands)
    new_list = list(name for name in commands if name not in old_list)

    textline = '--------------------\n'
    if miss_list:
       textline = textline + 'Disappeared commands: \n' + '\n'.join(miss_list) + '\n'
    if new_list:
       textline = textline + 'New commands: \n' + '\n'.join(new_list)
    if not miss_list and not new_list:
        textline = textline + 'No changes'

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = textline
    reply['type'] = msg['type']
    reply.send()

    return True

def secret():
    return True