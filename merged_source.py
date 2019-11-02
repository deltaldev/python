#### <module> bot.py ####
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from tools import Debug, Handler

db = Debug('main')

def server():
    bot_session = vk_api.VkApi(token = '9cda2485cc311a9de96a60797b9d4c35c3eea2be9cb2559244f69e11cdb7ccecebf399242b47d9f92f6ba')
    vk = bot_session.get_api()

    while True:
        longpoll = VkBotLongPoll(bot_session, 187703257)
        db.msg('STARTED')
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.obj.message['from_id'] > 0:
                    handler = Handler(event.obj.message['peer_id'], vk.users.get(user_ids = event.obj.message['from_id'])[0])
                    handler.drop(event.obj.message['text'])

if __name__ == '__main__':
    server()

#### <module> apis.py ####
def get_weather(place):
    import pyowm
    import json
    import bs4
    owm = pyowm.OWM(API_key = 'a907b822f169f2d235e52a52d63949b8', language = 'ru')
    observe, weather = None, None
    try:
        observe = owm.weather_at_place(place)
        weather = observe.get_weather()
        weather_temperature = weather.get_temperature('celsius')
        weather_details = weather.get_detailed_status()
        weather_details = weather_details[0].upper() + weather_details[1:]
        return [weather_temperature, weather_details]
    except Exception:
        pass
def get_wiki(txt):
    import wikipedia
    wikipedia.set_lang('ru')
    try:
        return wikipedia.summary(txt, sentences = 10)
    except Exception:
        pass

#### <module> tools.py ####
import vk_api, datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from requests import *
from apis import *
from random import randint

bot_session = vk_api.VkApi(token = '9cda2485cc311a9de96a60797b9d4c35c3eea2be9cb2559244f69e11cdb7ccecebf399242b47d9f92f6ba')
vk = bot_session.get_api()

def send(user_id = None, chat_id = None, peer_id = None, message = None, attachment = None):
    vk.messages.send(
        user_id = user_id,
        chat_id = chat_id,
        peer_id = peer_id,
        message = message,
        attachment = attachment,
        random_id = 0
    )
def has_in(list_, v):
    for i in range(len(list_)):
        if list_[i] in v:
            return True

class Debug:
    def __init__(self, label):
        self.trace_c = 0
        self.trace_p = []
        self.label = label
    def msg(self, x):
        print('[{}] ({}) {}'.format(self.label, self.trace_c, x))
        self.trace_p.append(x)
        self.trace_c += 1

db = Debug('tools')

class Handler:
    def __init__(self, receiver, user):
        self.catching = [['кекка даке га'], ['d32742'], ['5h1r0'], ['4d33ry'], ['d1nr3d'], ['4z4m47'], ['y4r1k']]
        self.commands = ['-погода', '-вики', '-когда', '-проверка']
        self.receiver = receiver
        self.user = user
    def drop(self, msg):
        db.msg('dropped')
        name = self.user['first_name']
        if len(msg) > 0:
            if msg[0] != '-':
                if has_in(self.catching[0], msg.lower()):
                    send(peer_id = self.receiver, message = 'KYONOU KEKKA DAKE GA NO KORU', attachment = 'photo414233360_457241949')
                elif has_in(self.catching[1], msg.lower()):
                    x = vk.users.get(user_ids = 244494455, fields = ['photo_id'])[0]['photo_id']
                    send(peer_id = self.receiver, message = 'Deltal', attachment = f'photo{x}')
                elif has_in(self.catching[2], msg.lower()):
                    x = vk.users.get(user_ids = 410685632, fields = ['photo_id'])[0]['photo_id']
                    send(peer_id = self.receiver, message = 'Shiro Sakino', attachment = f'photo{x}')
                elif has_in(self.catching[3], msg.lower()):
                    x = vk.users.get(user_ids = 268658637, fields = ['photo_id'])[0]['photo_id']
                    send(peer_id = self.receiver, message = 'Adeery', attachment = f'photo{x}')
                elif has_in(self.catching[4], msg.lower()):
                    x = vk.users.get(user_ids = 414233360, fields = ['photo_id'])[0]['photo_id']
                    send(peer_id = self.receiver, message = 'Din Red', attachment = f'photo{x}')
                elif has_in(self.catching[5], msg.lower()):
                    x = vk.users.get(user_ids = 245524320, fields = ['photo_id'])[0]['photo_id']
                    send(peer_id = self.receiver, message = 'Азамат Галлямутдинов', attachment = 'photo244494455_457251667')
                elif has_in(self.catching[6], msg.lower()):
                    x = vk.users.get(user_ids = 494560105, fields = ['photo_id'])[0]['photo_id']
                    send(peer_id = self.receiver, message = 'Азамат Галлямутдинов', attachment = 'photo244494455_457251667')
            else:
                cmd = msg.split(' ', 1)[0]
                arg = None
                if len(msg.split(' ', 1)) > 1:
                    arg = msg.split(' ', 1)[1]
                print(cmd, arg)
                if cmd == self.commands[0]:
                    weather = get_weather(arg)
                    if weather == None:
                        send(peer_id = self.receiver, message = f'{name}, по городу "{arg}" ничего не найдено 😓')
                    else:
                        send(peer_id = self.receiver, message = f'{name}, погода для города {arg} ☁: {weather[0]["temp"]}°C, {weather[1]}. ')
                elif cmd == self.commands[1]:
                    answer = get_wiki(arg)
                    if answer == None:
                        send(peer_id = self.receiver, message = f'{name}, Ничего не найдено 😓')
                    else:
                        send(peer_id = self.receiver, message = f'{name}, вот что я нашла: {answer}')
                elif cmd == self.commands[2]:
                    now = datetime.datetime.now()
                    def get_random_date():
                        map_ = {
                            1: 31,
                            2: 28,
                            3: 31,
                            4: 30,
                            5: 31,
                            6: 30,
                            7: 31,
                            8: 31,
                            9: 30,
                            10: 31,
                            11: 30,
                            12: 31
                        }
                        random_year = randint(now.year, now.year + 5)
                        random_month = randint(1, 12)
                        random_day = randint(1, map_[random_month])
                        if random_month < now.month and random_year == now.year:
                            random_year += 1
                        if random_day < 10:
                            random_day = '0' + str(random_day)
                        if random_month < 10:
                            random_month = '0' + str(random_month)
                        return f'{random_day}.{random_month}.{random_year}'
                    send(peer_id = self.receiver, message = f'{name}, {get_random_date()} 📅')
                elif cmd == self.commands[3]:
                    send(peer_id = self.receiver, message = 'Доступ есть ☺')
                else:
                    send(peer_id = self.receiver, message = f'{name}, не такой комманды 😓')