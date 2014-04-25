__author__ = 'hoochy'
import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp, eve

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
                        #hoochy
            if 'die!' in msg['body']:
                self._disconnect()

            if 'allert!' in msg['body']:

                reply = xmpp.make_message(msg['from'], mbody = 'Запрашиваем данные с сервера. Подождите...', mtype='chat')
                reply.send()

                for line in self.eve.get_notifications():
                    reply = xmpp.make_message(msg['from'], mbody = line, mtype='chat')
                    reply.send()
                    #xmpp.send_message(mto=msg['from'],
                    #      mbody=self.msg,
                    #      mtype='chat')
                    #msg.reply(line).send()
                return
            if 'help!' in msg['body']:

                reply = xmpp.make_message(msg['from'], mbody = 'Доступные команды: \nhelp!\nallert!', mtype='chat')
                reply.send()
                return
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

#создаем интерфейс в еву
eve = eve.eve()

#создаем бота
jid = "stormbp@jb.legionofdeath.ru"
password = "123newpass321"

xmpp = EchoBot(jid, password)
xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0004') # Data Forms
xmpp.register_plugin('xep_0060') # PubSub
xmpp.register_plugin('xep_0199') # XMPP Ping

xmpp.eve = eve

# If you are working with an OpenFire server, you may need
# to adjust the SSL version used:
# xmpp.ssl_version = ssl.PROTOCOL_SSLv3

# If you want to verify the SSL certificates offered by a server:
# xmpp.ca_certs = "path/to/ca/cert"

# Connect to the XMPP server and start processing XMPP stanzas.
if xmpp.connect():
    # If you do not have the dnspython library installed, you will need
    # to manually specify the name of the server if it does not match
    # the one in the JID. For example, to use Google Talk you would
    # need to use:
    #
    # if xmpp.connect(('talk.google.com', 5222)):
    #     ...
    xmpp.process(block=True)
    print("Done")
else:
    print("Unable to connect.")


#играемся
#alliance_list() #создаем базу альянсов
#get_wallet()
#solar_system_list()
#get_notifications()