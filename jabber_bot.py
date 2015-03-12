__author__ = 'hoochy'
import sys
import sleekxmpp
from sleekxmpp.xmlstream import ET

class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        #запомним свое имя
        self.nick = self.boundjid.user

        #словарь соответсвия ников в комнатах реальным джидам
        self.dict_of_real_JID = {}

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

    def cron(self, **kwargs):

        if "plugin" in kwargs:
            plugin = kwargs['plugin']
        else:
            return
        module = getattr(self.plugins['storage'], plugin)
        body = module.exec(bot = self, msg = None, ReplyTo = None, auth = None, param = None)

        #получим список комнат куда спамить
        try:
            rooms = module.rooms()
            allrooms = False
        except:
            allrooms = True

        if not body:
            return
        body = '\n' + '*'*40 + '\n' + body + '\n' + '*'*40
        #бежим по комнатам где сидим
        for room in self.plugin['xep_0045'].rooms:
            #print(allrooms)
            #print(rooms)
            if room == self.botroom + '@conference.jb.legionofdeath.ru':
                continue

            if not allrooms:
                if not room in rooms:
                    continue

            ReplyTo = sleekxmpp.JID(room)
            reply = self.make_message(ReplyTo)
            reply['body'] = body
            reply['type'] = 'groupchat'
            reply.send()


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
        #self.schedule('notif', 15, self.check_notif, repeat = True)
        #проверяем плагин на наличие шедулера и шедулим если есть.
        for command in self.plugins['commands']:
            module = getattr(self.plugins['storage'],command)
            try:
                schedule = module.schedule()
                if schedule > 0:
                    self.schedule('cron_' + command, schedule, self.cron, repeat = True, kwargs = {'plugin':command})
            except:
                pass

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
        if msg['mucnick'] == self.nick or msg['mucnick'] == self.mucnick:
            return

        if msg['type'] in ('chat', 'normal', 'groupchat'):

            if 'die!' == msg['body']:
                self._disconnect()
            elif 'зло' == msg['body']:
                self.censor = True

            #получим первое слово сообщения
            temp_list = msg['body'].split(' ')
            command = temp_list[0]
            #проверим есть ли параметры
            param = None
            if len(temp_list) > 1:
                param = temp_list[1:]
            #будем сообщать о сообщениях боту в приват или о командах в конфах
            if msg['type'] in ('chat', 'normal') or (msg['type'] == 'groupchat' and command in self.plugins['commands']):
                ReplyTo = sleekxmpp.JID(self.botroom + '@conference.jb.legionofdeath.ru')
                reply = self.make_message(ReplyTo)
                if msg['type'] in ('chat', 'normal'):
                    textline = 'Личное сообщение от ' + msg['from'].full + '\n' + msg['body']
                else:
                    textline = 'Команда в комнате ' + msg['mucroom'] + ' от ' + msg['from'].resource + '\n' + msg['body']

                reply['body'] = textline
                reply['type'] = 'groupchat'
                reply.send()

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

                admin = self.is_admin(self.JID_to_realJID(msg))

                if secret and admin:
                    module.exec(bot = self, msg = msg, ReplyTo = ReplyTo, auth = None, param = param)
                elif secret and (not admin):
                    msg.reply("Access denied to command \n%(body)s" % msg).send()
                elif not secret:
                    module.exec(bot = self, msg = msg, ReplyTo = ReplyTo, auth = None, param = param)

            else:
                pass
                #if not msg['type'] == 'groupchat':
                    #pass
                    #msg.reply("Thanks for sending\n%(body)s" % msg).send()

        return

    def form_message(self, msg):

        if msg['form']['type'] == 'submit':
            #не нашел способа узнать что за форма, проверяю по наличию поля в форме
            if "Broadcast" in msg['form']['values']:

                items = msg['form']['values']['Group'].split(';')
                for item in items:
                    toJID = sleekxmpp.JID(jid=item + '@broadcast.jb.legionofdeath.ru')
                    #toJID = sleekxmpp.JID('test@broadcast.jb.legionofdeath.ru')

                    reply = self.make_message(toJID, 'Broadcast from '+ self.JID_to_realJID(msg).bare + ' to ' + item + '\n' + msg['form']['values']['Broadcast'], mtype='normal')
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

    def muc_presense(self, presence):

        #presence['type'] 'available' 'unavailable'

        if presence['muc']['nick'] != self.mucnick:
            if presence['type'] == 'unavailable':
                del(self.dict_of_real_JID[presence['muc']['room'] + '/' + presence['muc']['nick']])
            else:
                self.dict_of_real_JID[presence['muc']['room'] + '/' + presence['muc']['nick']] = presence['muc']['jid'].bare
        if presence['muc']['room'] and presence['type'] != 'unavailable':
            self.check_nick(presence)

    def muc_online(self, presence):
        pass

    def check_nick(self, presence):

        if not self.censor:
            return

        if presence['muc']['nick'] != self.mucnick:
            jid = presence['muc']['jid'].bare
            module = getattr(self.plugins['storage'], 'muc_censor')
            correct_name = module.exec(bot = self, msg = None, ReplyTo = None, auth = None, param = (jid,))
            if correct_name and correct_name != presence['muc']['nick']:
                #ругаемся что ник надо поправить
                ReplyTo = sleekxmpp.JID(presence['muc']['room'])
                reply = self.make_message(ReplyTo)
                reply['body'] = '' + presence['muc']['nick'] + ' поменяй ник на ' + correct_name + '\nЕсли считаешь что ник корректный, обнови API ключ на http://dashboard.legionofdeath.ru'
                reply['type'] = 'groupchat'
                reply.send()
                #пробуем насильно поменять ник
                stanza = self.makePresence()
                x = ET.Element('{http://jabber.org/protocol/muc#user}x')
                itemXML = ET.Element('item', {'affiliation': 'owner', 'jid': presence['muc']['jid'].full, 'role':'moderator'})
                x.append(itemXML)
                itemXML = ET.Element('status ', {'code': '110',})
                x.append(itemXML)
                itemXML = ET.Element('status ', {'code': '210',})
                x.append(itemXML)
                stanza.append(x)

                #if password:
                #    passelement = ET.Element('{http://jabber.org/protocol/muc}password')
                #    passelement.text = password
                #    x.append(passelement)
                #if maxhistory:
                #history = ET.Element('{http://jabber.org/protocol/muc}history')
                #if maxhistory ==  "0":
                #    history.attrib['maxchars'] = maxhistory
                #else:
                #    history.attrib['maxstanzas'] = maxhistory
                #x.append(history)
                #stanza.append(x)
                #if not wait:
                #    self.xmpp.send(stanza)
                #else:
                    #wait for our own room presence back
                #    expect = ET.Element("{%s}presence" % self.xmpp.default_ns, {'from':"%s/%s" % (room, nick)})
                #    self.xmpp.send(stanza, expect)
                #self.rooms[room] = {}
                #self.ourNicks[room] = nick
                #stanza['from'] = self.plugin['xep_0045'].rooms[presence['muc']['room']][self.mucnick]['jid']
                #stanza['from'] = sleekxmpp.JID(presence['muc']['room'] + '/oldhag')
                #stanza['id'] = 'D0E2B666-3373-42C9-B726-D52C40A48383'
                #stanza['to'] = presence['muc']['jid']
                #self.send(stanza)
                #stanza['status'] = pstatus
                #stanza['nick'] = pnick

    def JID_to_realJID(self, msg):

        if msg['from'].full in self.dict_of_real_JID:
            return sleekxmpp.JID(self.dict_of_real_JID[msg['from'].full])
        else:
            return msg['from']

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

    def one_day_delta_to_str(self, s):
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours == 0:
            if minutes == 0:
                return str('%d секудн назад' % (seconds))
            else:
                return str('%d минут %d секунд назад' % (minutes, seconds))
        else:
            return str('%d часов %d минут %d секунд назад' % (hours, minutes, seconds))