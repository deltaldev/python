## <file> bot.py (First connecting to api/catching errors/catching messages)


import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from handler import Debug, Handler

db = Debug('main')

def server():
    bot_session = vk_api.VkApi(token = '9cda2485cc311a9de96a60797b9d4c35c3eea2be9cb2559244f69e11cdb7ccecebf399242b47d9f92f6ba')
    vk = bot_session.get_api()

    while True:
        try:
            longpoll = VkBotLongPoll(bot_session, 187703257)
            db.msg('STARTED')
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.obj.message['from_id'] > 0:
                        if 'reply_message' in event.obj.message:
                            handler = Handler(event.obj.message['peer_id'], vk.users.get(user_ids = event.obj.message['from_id'], fields = ['sex'])[0], event.obj.message['reply_message'])
                            handler.drop(event.obj.message['text'])
                        else:
                            handler = Handler(event.obj.message['peer_id'], vk.users.get(user_ids = event.obj.message['from_id'], fields = ['sex'])[0], False)
                            handler.drop(event.obj.message['text'])
        except Exception as e:
            db.msg(f'ERR: {e}')

if __name__ == '__main__':
    server()


## <file> methods.py (Methods to use/side API's)


import pyowm, wikipedia, json, vk_api, re
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
wikipedia.set_lang('ru')
owm = pyowm.OWM(API_key = 'a907b822f169f2d235e52a52d63949b8', language = 'ru')
observe, weather = None, None
bot_session = vk_api.VkApi(token = '9cda2485cc311a9de96a60797b9d4c35c3eea2be9cb2559244f69e11cdb7ccecebf399242b47d9f92f6ba')
vk = bot_session.get_api()
ranks = [['Starter Ньюфаг', 0], ['Starter Петух', 5], ['Starter Боец', 10], ['Starter Розбойник', 15], ['Starter Гачи-боец', 20], ['Medium Татар', 30], ['Medium Узбек', 40], ['Medium Самурай', 50], ['Medium Латекс-бой', 60], ['High Турник-мен', 80], ['High Каратист', 100], ['High Сенсей', 120], ['High Станд-юзер', 140], ['Insane Джокер', 180], ['Insane Куколд', 220], ['Insane Админ', 260], ['Insane Твоя Мамка', 300], ['Mythical Вампир', 380], ['Mythical Инфернал', 460], ['Mythical Титан', 540], ['Mythical Хранитель', 620], ['Master Путин', 780], ['Master Генос', 940], ['Master Ванпанчмен', 1100], ['Master Бог', 1260]]
def get_weather(place):
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
    try:
        return wikipedia.summary(txt, sentences = 5)
    except Exception:
        pass
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
def charcount(c, s):
    count = 0
    for i in range(len(s)):
        if s[i] == c:
            count += 1
    return count
def openjson(f):
    return json.loads(open(f).read())
def rewritejson(f, d):
    open(f, 'w').write(d)
def replace_nicknames(a):
    s = a
    r = ''
    nicknames = openjson('nicknames.json')
    for i in range(len(s)):
        if s[i] == '[':
            for j in range(i + 1, len(s)):
                if s[j] != '|':
                    r += s[j]
                else:
                    break
            if r[2:] not in nicknames and r[4:] not in nicknames:
                if 'id' in r:
                    name = vk.users.get(user_ids = r[2:])[0]['first_name']
                    nicknames[r[2:]] = name
                elif 'club' in r:
                    name = vk.groups.getById(group_ids = r[4:])[0]['name']
                    nicknames[r[4:]] = name
                rewritejson('nicknames.json', str(nicknames).replace("'", '"'))
                r = ''
            r = ''
    for k, v in nicknames.items():
        try:
            if s.index(k) != -1:
                for i in range(s.index(k) + len(k) + 1, len(s)):
                    if s[i] != ']':
                        r += s[i]
                    else:
                        break
            s = s.replace(f'[id{k}|{r}]', f'[id{k}|{v}]')
            r = ''
        except Exception as e:
            pass
    return s
def id_from_mention(a):
    if '[club' in a:
        return ''
    s = ''
    for i in range(len(a)):
        if a[i] == 'd':
            for j in range(i + 1, len(a)):
                if a[j] != '|':
                    s += a[j]
                else:
                    break
        if a[i] == '|':
            break
    return s
def del_comma_spaces(a):
    s = a
    for i in range(len(s)):
        try:
            if s[i] == ' ' and (s[i + 1] == ',' or s[i - 1] == ','):
                s2 = list(s)
                s2[i] = '¢'
                s = ''.join(str(e) for e in s2)
        except Exception as e:
            pass
    if s[len(s) - 1] == ' ':
        s2 = list(s)
        s2[len(s) - 1] = '¢'
        s = ''.join(str(e) for e in s2)
    s = s.replace('¢', '')
    return s
def del_mentions(a):
    s = ''
    inm = False
    for i in range(len(a)):
        if a[i] == '[':
            inm = True
        if a[i] == ']':
            inm = False
        else:
            if not inm:
                s += a[i]
    return s
def catch_mentions(a):
    s = []
    inm = False
    for i in range(len(a)):
        if a[i] == '[' and (a[i+1:i+3] == 'id' or a[i+1:i+5] == 'club'):
            nm = ''
            for j in range(i, len(a)):
                if a[j] == ']':
                    nm += a[j]
                    break
                nm += a[j]
            s.append(nm)
    return s
def isint(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
def inkeys(d, val):
    for k, v in d.items():
        if v == val:
            return True
    return False
def update_words(t):
    dictionary = openjson('words.json')
    msgwords = re.sub('([^A-Za-zА-Яа-я ё])', '', del_mentions(t.lower())).replace(',', '').replace('.', '').split(' ')
    for i in range(len(msgwords)):
        if msgwords[i] not in dictionary['list'] and len(msgwords[i]) <= 30:
            dictionary['list'].append(msgwords[i])
    rewritejson('words.json', str(dictionary).replace("'", '"'))
def process_message(t, c):
    iscommand = False
    if t[:26] == '[club187703257|@botwaifu] ':
        t = c + t[26:]
        iscommand = True
    if t[:6].lower() == c:
        iscommand = True
    nicknames = openjson('nicknames.json')
    mentions = catch_mentions(t)
    for i in range(len(mentions)):
        mentions[i] = replace_nicknames(mentions[i])
    return {'processed': replace_nicknames(t), 'mentions': mentions, 'iscommand': iscommand}
def process_command(t):
    t = t[6:]
    print(t)
    cmd, arg = t.split(' ', 1)[0], None
    if len(t.split(' ', 1)) > 1:
        arg = t.split(' ', 1)[1]
    return {'cmd': cmd, 'arg': arg}


## <file> handler.py (Message handler/sender)


import vk_api, datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from methods import *
from random import randint, choice

bot_session = vk_api.VkApi(token = '9cda2485cc311a9de96a60797b9d4c35c3eea2be9cb2559244f69e11cdb7ccecebf399242b47d9f92f6ba')
vk = bot_session.get_api()

class Debug:
    def __init__(self, label):
        self.trace_c = 0
        self.trace_p = []
        self.label = label
    def msg(self, x):
        print('[{}] ({}) {}'.format(self.label, self.trace_c, x))
        self.trace_p.append(x)
        self.trace_c += 1

db = Debug('handler')

class Handler:
    def __init__(self, receiver, user, rep):
        self.catching = [['иди нахуй', 'нахуй иди', 'пошёл нахуй', 'нахуй пошёл'], ['прости', 'извини', 'sorry', 'сорян', 'сорри', 'извините'], ['соси', 'сосать', 'сасать', 'сосатб', 'сасатб', 'саси'], ['гей', 'геи']]
        self.receiver = receiver
        self.user = user
        self.sex = self.user['sex']
        self.id = self.user['id']
        self.rep = rep
        self.comma = 'вайфу '
    def drop(self, msg):
        if len(msg) > 0:
            msg = process_message(msg, self.comma)
            msg_text = msg['processed']
            mentions = msg['mentions']
            name = replace_nicknames(f'[id{self.id}|user]')
            if msg['iscommand']:
                call = process_command(msg_text)
                cmd = call['cmd']
                arg = call['arg']
                # <command> погода
                if cmd.lower() == 'погода':
                    weather = get_weather(arg)
                    if weather == None:
                        send(peer_id = self.receiver, message = f'{name}, по городу "{arg}" ничего не найдено 😓')
                    else:
                        send(peer_id = self.receiver, message = f'{name}, погода для города {arg} ☁: {weather[0]["temp"]}°C, {weather[1]}. ')
                # <command> вики
                elif cmd.lower() == 'вики':
                    answer = get_wiki(arg)
                    if answer == None:
                        send(peer_id = self.receiver, message = f'{name}, по запросу "{arg}" ничего не найдено 😓')
                    else:
                        send(peer_id = self.receiver, message = f'{name}, вот что я нашла: {answer}')
                # <command> бой
                elif cmd.lower() == 'бой':
                    intros = [
                        '{}: Эй, {}, бросай свои дела и сразись со мной в эпичном поединке! ',
                        '{}: Эй ты, {}, думаешь сильнее меня? Давай сразимся! ',
                        '{}: Сразу же атакует бойца {}! ',
                    ]
                    duels = [
                        'Они выбрали бой в рукопашку, один из них покажет кто тут сенсей! ',
                        'Они выбрали бой флексом, один из них покажет кто тут великий флексер! ',
                        'Они выбрали бой на мечах, один из них покажет кто тут мастер фехтования! '
                    ]
                    endings = [
                        'В битве боевых искусств победителем выходит {}, боец {} был отправлен в нокаут!',
                        'В битве флекса победителем выходит {}, боец {} был снесен с ног невероятным флексом!',
                        'В битве на мечах победителем выходит {}, бойца {} решили головы!'
                    ]
                    mention = None
                    if not self.rep:
                        if arg != None:
                            if len(mentions) > 0:
                                mention = mentions[0]
                    else:
                        rep_id = self.rep['from_id']
                        mention = replace_nicknames(f'[id{rep_id}|user]')
                    if mention != None:
                        if name == mention:
                            send(peer_id = self.receiver, message = f'{name}, я думаю тебе стоит завести друзей 😓')
                        else:
                            ratings = openjson('ratings.json')
                            your_id = str(self.id)
                            mention_id = id_from_mention(mention)
                            if your_id not in ratings:
                                ratings[your_id] = {"wins": 0, "rank": ["Starter Ньюфаг", 1]}
                                your_rating = 0
                            else:
                                your_rating = ratings[your_id]['wins']
                            if mention_id not in ratings:
                                ratings[mention_id] = {"wins": 0, "rank": ["Starter Ньюфаг", 1]}
                                mention_rating = 0
                            else:
                                mention_rating = ratings[mention_id]['wins']
                            x = randint(0, 2)
                            intro, duel, ending, addrates = choice(intros).format(name, mention), duels[x], endings[x], '\n\n{}: {}(+1)\n{}: {}(+0)'
                            winner = choice([name, mention])
                            if winner == mention:
                                winner_id = mention_id
                                loser = name
                                loser_id = your_id
                            else:
                                winner_id = your_id
                                loser = mention
                                loser_id = mention_id
                            ratings[winner_id]['wins'] += 1
                            for i in range(1, len(ranks) + 1):
                                if ratings[winner_id]['wins'] >= ranks[i - 1][1] and i > ratings[winner_id]['rank'][1]:
                                    ratings[winner_id]['rank'][0] = ranks[i - 1][0]
                                    ratings[winner_id]['rank'][1] += 1
                                    break
                            ending = ending.format(winner, loser)
                            addrates = addrates.format(winner, ratings[winner_id]['wins'], loser, ratings[loser_id]['wins'])
                            rewritejson('ratings.json', str(ratings).replace("'", '"'))
                            send(peer_id = self.receiver, message = intro + duel + ending + addrates)
                # <command> имя
                elif cmd.lower() == 'имя':
                    if arg != None:
                        new_name = arg.replace("'", '').replace('"', '').replace(',', '')
                        if new_name == '':
                            send(peer_id = self.receiver, message = f'{name}, попробуй имя без кавычек и запятых.')
                        else:
                            new = openjson('nicknames.json')
                            if inkeys(new, new_name):
                                send(peer_id = self.receiver, message = f'{name}, такое имя уже занято 😓')
                            else:
                                new[str(self.user['id'])] = arg.replace("'", '').replace('"', '')
                                rewritejson('nicknames.json', str(new).replace("'", '"'))
                                send(peer_id = self.receiver, message = f'Хорошо, теперь я буду называть тебя [id{self.id}|{arg}]!')
                # <command> рулетка
                elif cmd.lower() == 'рулетка':
                    if arg != None:
                        nums = arg.split(' ', 1)
                        if len(nums) == 2:
                            if isint(nums[0]) and isint(nums[1]):
                                send(peer_id = self.receiver, message = f'{name}, рулетка выдала {randint(int(nums[0]), int(nums[1]))}!')
                # <command> шар
                elif cmd.lower() == 'шар':
                    if arg == None:
                        send(peer_id = self.receiver, message = f'{name}, крутится вертится шар голубой...')
                    else:
                        if ' или ' in arg.lower():
                            between = arg.split(' или ')
                            send(peer_id = self.receiver, message = f'{name}, думаю {between[randint(0, len(between) - 1)]}')
                        elif arg.lower()[:5] == 'когда':
                            now = datetime.datetime.now()
                            def get_random_time():
                                type_ = ['сек.', 'мин.', 'ч.', 'д.', 'мес.', 'г.']
                                type_ = type_[randint(0, 5)]
                                count = None
                                rset = ''
                                if type_ == 'сек.' or type_ == 'мин.':
                                    count = randint(1, 60)
                                elif type_ == 'ч.':
                                    count = randint(1, 24)
                                elif type_ == 'д.':
                                    count = randint(1, 31)
                                    rset = f' в {randint(0,23)}:{randint(0,59)}'
                                elif type_ == 'мес.':
                                    count = randint(1, 12)
                                    rset = f' в {randint(0,23)}:{randint(0,5)}{randint(0,9)}'
                                elif type_ == 'г.':
                                    count = randint(1, 10)
                                    rset = f' в {randint(0,23)}:{randint(0,59)}'
                                    if count > 4:
                                        type_ = 'лет'
                                return f'{count} {type_}{rset}'
                            send(peer_id = self.receiver, message = f'{name}, через {get_random_time()}')
                        elif arg.lower()[:3] == 'кто' or arg.lower()[:4] == 'кого':
                            if self.id == self.receiver:
                                send(peer_id = self.receiver, message = f'{name}, выбор "кто/кого" работает только в беседах.')
                            else:
                                chat = vk.messages.getConversationMembers(peer_id = self.receiver)['profiles']
                                who = chat[randint(0, len(chat) - 1)]
                                who_id = who['id']
                                if 'first_name' in who:
                                    who_name = who['first_name']
                                    who = replace_nicknames(f'[id{who_id}|{who_name}]')
                                else:
                                    who_name = who['name']
                                    who = replace_nicknames(f'[club{who_id}|{who_name}]')
                                send(peer_id = self.receiver, message = f'{name}, думаю это {who}')
                        else:
                            answers = ['да', 'нет']
                            send(peer_id = self.receiver, message = f'{name}, думаю {answers[randint(0,1)]}')
                # <command> фраза
                elif cmd.lower() == 'фраза':
                    dictionary = openjson('words.json')['list']
                    end = ['.', '!', '?']
                    if arg == None:
                        count = randint(1, 20)
                        phrase = ''
                        for i in range(count):
                            phrase += dictionary[randint(0, len(dictionary) - 1)] + ' '
                        phrase = phrase[:-1]
                        phrase = phrase[0].upper() + phrase[1:] + end[randint(0, 2)]
                        send(peer_id = self.receiver, message = phrase)
                    else:
                        if isint(arg):
                            if int(arg) > 50:
                                send(peer_id = self.receiver, message = f'{name}, лимит фраз - 50.')
                            else:
                                count = int(arg)
                                phrase = ''
                                for i in range(count):
                                    phrase += dictionary[randint(0, len(dictionary) - 1)] + ' '
                                phrase = phrase[:-1]
                                phrase = phrase[0].upper() + phrase[1:] + end[randint(0, 2)]
                                send(peer_id = self.receiver, message = phrase)
                        else:
                            if len(arg.split(' ', 1)) > 1 and isint(arg.split(' ', 1)[0]) and not isint(arg.split(' ', 1)[1]):
                                phrase = ''
                                count = int(arg.split(' ', 1)[0])
                                includes = arg.split(' ', 1)[1]
                                for i in range(count):
                                    w = dictionary[randint(0, len(dictionary) - 1)]
                                    have = False
                                    for i in range(len(dictionary)):
                                        if includes in dictionary[i]:
                                            have = True
                                            break 
                                    if have:
                                        while includes not in w:
                                            w = dictionary[randint(0, len(dictionary) - 1)]
                                        phrase += w + ' '
                                phrase = phrase[:-1]
                                phrase = phrase[0].upper() + phrase[1:] + end[randint(0, 2)]
                                if phrase != '':
                                    send(peer_id = self.receiver, message = phrase)
                # <command> профиль
                elif cmd.lower() == 'профиль':
                    nicknames = openjson('nicknames.json')
                    ratings = openjson('ratings.json')
                    mention = None
                    intro = 'профиль пользователя {}'
                    if arg == None:
                        if not self.rep:
                            mention = name
                            mention_id = str(self.id)
                            intro = 'ваш профиль'
                        else:
                            mention_id = str(self.rep['from_id'])
                            mention = replace_nicknames(f'[id{mention_id}|user]')
                    else:
                        if len(mentions) > 0:
                            mention = mention[0]
                            mention_id = id_from_mention(mention)
                            if mention == name:
                                intro = 'ваш профиль'
                    nickname = nicknames[mention_id]
                    if mention_id not in ratings:
                        ratings[mention_id] = {"wins": 0, "rank": ["Starter Ньюфаг", 1]}
                        rating = 0
                        battle_rank = 'Starter Ньюфаг'
                        ranks_unlocked = 1
                    else:
                        rating = ratings[mention_id]['wins']
                        battle_rank = ratings[mention_id]['rank'][0]
                        ranks_unlocked = ratings[mention_id]['rank'][1]
                    wins_to_rank = 0
                    for i in range(1, len(ranks) + 1):
                        if i == ratings[mention_id]['rank'][1] + 1:
                            wins_to_rank = ranks[i - 1][1] - ratings[mention_id]['wins']
                    send(peer_id = self.receiver, message = f'{name}, это {intro.format(mention)}:\n\nНикнейм: {nickname}\nПобед в боях: {rating}\nРанг в боях: {battle_rank}({ranks_unlocked}/25, побед до нового ранга - {wins_to_rank})')
                # <command> топ
                elif cmd.lower() == 'топ':
                    ratings = openjson('ratings.json')
                    top = ''
                    for i in range(1, len(ratings) + 1 if len(ratings) <= 5 else 6):
                        max_ = 0
                        last_key = ''
                        for k, v in ratings.items():
                            if v['wins'] > max_:
                                max_ = v['wins']
                                last_key = k
                        del ratings[last_key]
                        nickname = replace_nicknames(f'[id{last_key}|user]')
                        top += f'{i} место: {nickname} - {max_}\n'
                    send(peer_id = self.receiver, message = f'{name}, это топ побед:\n\n{top}')
                # <command> рп
                elif cmd.lower() == 'рп':
                    if arg != None:
                        send(peer_id = self.receiver, message = f'{name} {arg}')
                # <command> стих
                elif cmd.lower() == 'стих':
                    dictionary = openjson('words.json')['list']
                    phrase = ''
                    if arg == None:
                        count = randint(1, 20)
                    else:
                        if isint(arg):
                            if int(arg) > 8:
                                send(peer_id = self.receiver, message = f'{name}, лимит строф - 8.')
                            else:
                                count = int(arg)
                    prev_end = ''
                    for i in range(1, count * 2 + 1):
                        stroke = ''
                        prev = ''
                        for j in range(1, 5):
                            w = dictionary[randint(0, len(dictionary) - 1)]
                            if len(prev) < 3:
                                while len(w) < 3:
                                    w = dictionary[randint(0, len(dictionary) - 1)]
                            if j == 4:
                                while len(w) < 3:
                                    w = dictionary[randint(0, len(dictionary) - 1)]
                                if i % 2 != 0:
                                    nice = False
                                    while not nice:
                                        for i in range(len(dictionary)):
                                            if dictionary[i][-3:] == w[-3:]:
                                                nice = True
                                        if not nice:
                                            while len(w) < 3:
                                                w = dictionary[randint(0, len(dictionary) - 1)]
                                else:
                                    while w[-3:] != prev_end[-3:]:
                                        w = dictionary[randint(0, len(dictionary) - 1)]
                                prev_end = w
                                print(prev_end)
                            stroke += w + ' '
                            prev = w
                        if i % 2 == 0:
                            phrase += stroke[0].upper() + stroke[1:-1] + '.\n'
                        else:
                            phrase += stroke[0].upper() + stroke[1:-1] + ',\n'
                    send(peer_id = self.receiver, message = phrase) 
            else:
                if 'или' in msg_text.lower() and charcount(' ', msg_text.lower()) == 2:
                    between = msg.split(' или ')
                    if between[1][-1] == '?' or between[1][-1] == '!' or between[1][-1] == '.':
                        send(peer_id = self.receiver, message = f'{name}, {between[randint(0,1)][:-1]}')
                    else:
                        send(peer_id = self.receiver, message = f'{name}, {between[randint(0,1)]}')
                elif has_in(self.catching[0], msg_text.lower()):
                    if self.sex == 2:
                        send(peer_id = self.receiver, message = f'Сам иди нахуй, {name} 😡')
                    else:
                        send(peer_id = self.receiver, message = f'Сама иди нахуй, {name} 😡')
                elif has_in(self.catching[1], msg_text.lower()):
                    send(peer_id = self.receiver, message = f'Sorry for what, {name}?')
                elif has_in(self.catching[2], msg_text.lower()):
                    if self.sex == 2:
                        send(peer_id = self.receiver, message = f'Сам соси, {name}😡')
                    else:
                        send(peer_id = self.receiver, message = f'Сама соси, {name} 😡')
                elif has_in(self.catching[3], msg_text.lower()):
                    if self.sex == 2:
                        send(peer_id = self.receiver, message = f'Сам ты гей, {name}😡')
                    else:
                        send(peer_id = self.receiver, message = f'Сама ты гей, {name} 😡')
            update_words(msg_text)
