__author__ = 'hoochy'
import sys
import sleekxmpp

class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

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
        if msg['type'] in ('chat', 'normal'):

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
                module.exec(bot = self, msg = msg, ReplyTo = None, auth = None, param = param)
            else:
                msg.reply("Thanks for sending\n%(body)s" % msg).send()

        return