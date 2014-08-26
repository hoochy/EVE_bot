__author__ = 'hoochy'
import sys
import sleekxmpp

class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        #запомним свое имя
        self.nick = self.boundjid.user

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        # переношу обработчик в основной модуль
        self.add_event_handler("message", self.message)

        #обработчик ответов через форму
        self.add_event_handler("message_xform", self.form_message)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        #свои сообщения в групчатах сразу игнорим
        if msg['mucnick'] == self.nick:
            return

        if msg['type'] in ('chat', 'normal', 'groupchat'):

            if 'die!' in msg['body']:
                self._disconnect()

            #получим первое слово сообщения
            temp_list = msg['body'].split(' ')
            command = temp_list[0]
            #проверим есть ли параметры
            param = None
            if len(temp_list) > 1:
                param = temp_list[1:]
            if command in self.plugins['commands']:
                module = getattr(self.plugins['storage'],command)
                #проверим команду на доступность всем
                try:
                    secret = module.secret()
                except:
                    secret = False

                #если сообщение из комнаты, заполним ReplyTo
                if msg['mucroom']:
                    ReplyTo = sleekxmpp.JID(msg['mucroom'])
                else:
                    ReplyTo = None

                if secret and self.is_admin(msg['from']):
                    module.exec(bot = self, msg = msg, ReplyTo = ReplyTo, auth = None, param = param)
                elif secret and (not self.is_admin(msg['from'])):
                    msg.reply("Access denied to command \n%(body)s" % msg).send()
                elif not secret:
                    module.exec(bot = self, msg = msg, ReplyTo = ReplyTo, auth = None, param = param)

            else:
                if not msg['type'] == 'groupchat':
                    msg.reply("Thanks for sending\n%(body)s" % msg).send()

        return

    def form_message(self, msg):

        if msg['form']['type'] == 'submit':
            #не нашел способа узнать что за форма, проверяю по наличию поля в форме
            if "Broadcast" in msg['form']['values']:

                items = msg['form']['values']['Group'].split(';')
                for item in items:
                    toJID = sleekxmpp.JID(jid=item + '@broadcast.jb.legionofdeath.ru')
                    #toJID = sleekxmpp.JID('test@broadcast.jb.legionofdeath.ru')
                    reply = self.make_message(toJID, 'Broadcast from '+ msg['from'].bare + '\n' + msg['form']['values']['Broadcast'], mtype='normal')
                    #reply = self.make_message(toJID, 'fgh', mtype='normal')
                    reply.send()

                #отчитаемся о посылке бродкаста
                self.report(msg, 'Сделан бродкаст группе ' + msg['form']['values']['Group'])
            elif "GroupContent" in msg['form']['values']:

                group = msg['form']['values']['Group']
                group_content = msg['form']['values']['GroupContent']
                group_db = self.bases['group_db']
                #если контент пустой, группу надо удалить
                if group_content:
                    group_db.set_value_by_ID(group, group_content)
                    self.report(msg, "Group " + group + " now set to <" + group_content +">")
                else:
                    group_db._db_base.__delitem__(group)
                    self.report(msg, "Group " + group + " now deleted")

    def is_admin(self, JID):
        if JID.user == 'hoochy' or JID.user == 'kareriii' or JID.user == 'aungverdal':
            return True
        #elif '@conference.' in JID.full and ('hoochy' in JID.full or 'kareriii' in JID.full or 'aungverdal' in JID.full):
        #    return True
        else:
            return False

    def report(self, msg, body):
        if msg['mucroom']:
            ReplyTo = sleekxmpp.JID(msg['mucroom'])
        else:
            ReplyTo = msg['from']

        reply = self.make_message(ReplyTo, body, mtype = msg['type'])
        reply.send()