__author__ = 'hoochy'

def exec(bot = False, msg = None, ReplyTo = None, auth = None):

    if not bot or not msg:
        return False

    reply = bot.make_message(msg['from'], mbody = '--------------------\nCommands!!!: \n' + '\n'.join(bot.plugins['commands']), mtype='chat')
    reply.send()

    return True