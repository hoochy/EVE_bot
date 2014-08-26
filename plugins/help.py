__author__ = 'hoochy'

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    if not bot or not msg:
        return False

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if param_list:
        #есть параметры. или запрос помощи по плагину или ерунда. проверяем. значащим для нас является только первый параметр.
        #в параметре должно быть имя плагина по которому нужна помощь
        name = param_list[0]
        if name in bot.plugins['commands']:
            module = getattr(bot.plugins['storage'], name)
            try:
                textline = module.help()
            except:
                textline = '--------------------\nPlugin < ' + name + '> has no help!'
        else:
            textline = '--------------------\nPlugin < ' + name + '> not found!'
    else:
        #проверим отправителя на причастность к элите, если нет, список секретных команд прячем
        if bot.is_admin(msg['from']):
            textline = '--------------------\nCommands: \n' + '\n'.join(bot.plugins['commands'])
        else:
            difference = set(bot.plugins['commands']) - set(bot.plugins['secret_commands'])
            textline = '--------------------\nCommands: \n' + '\n'.join(difference)

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = textline
    reply['type'] = msg['type']
    reply.send()

    return True

def help():
    return '--------------------\nPlugin provides list of plugins and help information about others plugins\nusage:\n\
            help - list of plugins\n\
            help <name> - help information of plugin named <name>'