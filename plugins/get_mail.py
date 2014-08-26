__author__ = 'hoochy'
import datetime, re

def string_format(value):

    if type(value) == float:
        return "%0.0f" % value
    elif type(value) == int:
        return "%d" % value
    else:
        return "%s" % value

def remove_tags(data):
    #переводы строк заменям из тега на стандарт питона
    data = data.replace('<br>','\n')
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def exec(bot = False, msg = None, ReplyTo = None, auth = None, **kwargs):

    global localbot

    if not bot or not msg:
        return False

    localbot = bot

    #проверим пришли ли параметры
    if "param" in kwargs:
        param_list = kwargs['param']
    else:
        param_list = ()

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = '\nFetching mails...'
    reply['type'] = msg['type']
    reply.send()


    if param_list:
        #есть параметры. отдельно обработаем CTA

        textline = '\n' + '\n'.join(get_mails())

    else:
        textline = '\n' + '\n'.join(get_mails())

    if not textline:
        textline = '\nNo mails!'

    if not ReplyTo:
        reply = bot.make_message(msg['from'])
    else:
        reply = bot.make_message(ReplyTo)

    reply['body'] = textline
    reply['type'] = msg['type']
    reply.send()

    return True

def help():
    return '--------------------\nPlugin provides list of alliance mails \nusage:\n\
            get_mail - list of recent 10 mails\n\
            get_mail CTA ...- list of active CTA ...\n'

def get_mails():

    global localbot
    line = '-'*80
    #выводит письма
    result2 = localbot.eve.auth.account.Characters()

    news_line = []
    for character in result2.characters:
        MailID = localbot.eve.auth.char.MailMessages(characterID=character.characterID)
        count = 1
        for RowID in MailID.messages:
            toCorpOrAllianceID = string_format(RowID.toCorpOrAllianceID)
            if toCorpOrAllianceID == '1411711376':
                MailBody = get_mail_body_by_ID(characterID = character.characterID, mailID = RowID.messageID)
                news_line.append('Письмо № ' + string_format(count) + '\n' + remove_tags(line + '\nTitle = ' + string_format(RowID.title) + '\n' + line +
                        '\nDate = ' + string_format(datetime.datetime.fromtimestamp(RowID.sentDate)) +
                        '\n' + line +  "\n" + MailBody)+ '\n\n' )

                count += 1
            if count == 10:
                break

    return news_line

def get_mail_body_by_ID(characterID, mailID):

    global localbot

    #возвращает тело нитификации в виде строки по ключу авторизованному в auth, для сообщения с notificationID у чара characterID

    #здесь нужно сделать конструктор из долбанного формата ццп в читаемый текст для нужных типов сообщений (атака поса, установка сбу и т.п.)
    result = localbot.eve.auth.char.MailBodies(characterID=characterID, IDs=string_format(mailID))
    message = result.messages[0].data
    return message
