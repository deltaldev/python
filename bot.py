import json, requests, bs4, vk_api, urllib3, re
from datetime import datetime
from random import randint, choice
from threading import Thread
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType




token = "9cda2485cc311a9de96a60797b9d4c35c3eea2be9cb2559244f69e11cdb7ccecebf399242b47d9f92f6ba"
bot_session = vk_api.VkApi(token=token)
vk = bot_session.get_api()
 



def openjson(f):
    return json.loads(open(f).read())


def rewritejson(f, d):
    open(f, 'w').write(str(d).replace("'", '"'))


def getName(id_):
    names = openjson('names.json')
    if str(id_) not in names:
        if id_ > 0:
            return vk.users.get(user_ids=id_)[0]['first_name']
        else:
            return vk.groups.getById(group_ids=int(str(id_)[1:]))[0]['name']
    else:
        return names[str(id_)]


def getNamel(id_):
    if id_ > 0:
        return f'{getRole(id_)} [id{id_}|{getName(id_)}]'
    else:
        return f'{getRole(id_)} [club{str(id_)[1:]}|{getName(id_)}]'


def getRole(id_):
    roles = openjson('roles.json')
    if str(id_) in roles:
        return roles[str(id_)]
    return ''


def getRep(id_):
    respects = openjson('respects.json')
    if str(id_) in respects:
        return len(respects[str(id_)])
    return ''


def getFamily(id_):
    families = openjson('families.json')
    for k, v in families.items():
        if id_ in v['members']:
            return k
    return ''


def getRp(id_):
    rp = openjson('rp.json')
    if str(id_) not in rp:
        rp[str(id_)] = {
            'replics': 0,
            'actions': 0,
            'lastreplic': '',
            'lastaction': ''
        }
        rewritejson('rp.json', rp)
    return rp[str(id_)]


def getStats(id_):
    stats = openjson('stats.json')
    if str(id_) not in stats:
        stats[str(id_)] = {
            'cmds_called': 0,
            'nicknames_changed': 0,
            'roles_changed': 0,
            'respected': 0,
        }
        rewritejson('stats.json', str(stats).replace("'", '"'))
    return stats[str(id_)]
 

def updateStats(id_, key, additional):
    getStats(id_)
    stats = openjson('stats.json')
    stats[str(id_)][key] += additional
    rewritejson('stats.json', str(stats).replace("'", '"'))


def getRank(id_):
    rank = openjson('rank.json')
    if str(id_) not in rank:
        rank[str(id_)] = {
            'battles_completed': 0,
            'battles_won': 0,
            'rank': 'Ученик'
        }
        rewritejson('rank.json', str(rank).replace("'", '"'))
    return rank[str(id_)]
 

def updateRank(id_, key, additional):
    getrank(id_)
    rank = openjson('rank.json')
    rank[str(id_)][key] += additional
    rewritejson('rank.json', str(rank).replace("'", '"'))


def checkSpelling(string):
    admiss = True if 3 <= len(string) <= 40 else False
    alphabet = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя '
    for s in string:
        if s.lower() not in alphabet:
            admiss = False
    return admiss


def keyboard(*b):
    buttons = []
    for i in b:
        buttons.append([])
        for j in i:
            buttons[-1].append({
                'action': {
                    'type': 'text',
                    'label': j[0]
                },
                'color': j[1]
            })
    return json.dumps({'buttons': buttons, 'inline': True})


def tags(s):
    r, f = '', True
    for i in list(s):
        if f:
            if i == '<':
                f = False
            else:
                r += i
        else:
            if i == '>':
                f = True
    return r


def ids(m):
    if m:
        mentions = m.replace('[', '$sep').replace(']', '$sep').replace('|', '$sep').split('$sep')
        users = [int(m[2:]) for m in mentions if m[:2] == 'id' and m[2:].isdigit()]
        groups = [int('-' + m[4:]) for m in mentions if m[:4] == 'club' and m[4:].isdigit()]
        return users + groups
    return []


def parsementions(s):
    newstring = s
    nicknames = openjson('names.json')
    m = s.replace('[', '$sep').replace(']', '$sep').replace('|', '$sep').split('$sep')
    print(m)
    fs = []
    for i in range(len(m)):
        if fs:
            if m[i] in fs[-1]:
                continue
        if (m[i][:2] == 'id' and m[i][2:].isdigit()) or (m[i][:4] == 'club' and m[i][4:].isdigit()):
            fs.append([m[i], m[i + 1]])
    print(fs)
    for f in fs:
        digitid = int(f[0][2:]) if f[0][:2] == 'id' else int('-' + f[0][4:])
        nickname = getName(digitid)
        role = getRole(digitid)
        newstring = newstring.replace(f'[{f[0]}|{f[1]}]', f'{role} [{f[0]}|{nickname}]')
    return newstring


def getimage(url):
    http = urllib3.PoolManager()
    return {'file': (url, http.request('GET', url, preload_content=False).data)}


def getgif(url, count):
    http = urllib3.PoolManager()
    gifs = json.loads(requests.get(url).text)['data']
    if gifs:
        target = choice(gifs[:count])['images']['downsized']['url']
        return {'file': (target, http.request('GET', target, preload_content=False).data)}
    return None


def uploadfile(file, peer):
    server = vk.docs.getMessagesUploadServer(type='doc', peer_id=peer)
    uploaded_file = json.loads(requests.post(server['upload_url'], files=file).text)['file']
    doc = vk.docs.save(file=uploaded_file, title='asura-bot')['doc']
    id_, ownerid = doc['id'], doc['owner_id']
    return f'doc{ownerid}_{id_}'


def uploadimage(file, peer):
    server = vk.photos.getMessagesUploadServer(peer_id=peer)
    uploaded_file = json.loads(requests.post(server['upload_url'], files=file).text)
    photo = vk.photos.saveMessagesPhoto(
        server=uploaded_file['server'],
        photo=uploaded_file['photo'],
        hash=uploaded_file['hash'])[0]
    id_, ownerid = photo['id'], photo['owner_id']
    return f'photo{ownerid}_{id_}'


def getAvatar(id_, peer):
    if id_ > 0:
        resolve = vk.users.get(user_ids = id_, fields = ['photo_id'])[0]
        if 'photo_id' in resolve:
            return 'photo' + resolve['photo_id']
        else:
            return 'photo-187703257_457239149'
    else:
        resolve = vk.groups.getById(group_ids = str(id_)[1:], fields = ['photo_200'])[0]
        if 'photo_200' in resolve:
            return uploadimage(getimage(resolve['photo_200']), peer)
        else:
            return 'photo-187703257_457239149'

class Bot:
    def __init__(self, userId, peerId, chatId, reply):
        self.peer = peerId
        self.chat = chatId
        self.id = userId
        self.reply = reply
        self.name = getName(self.id)
        self.namel = getNamel(self.id)
        self.cmdsinfo = {
            'асура': 'ℹ асура <текст> - напиши мне что-нибудь!',
            'помощь': 'ℹ помощь - выдает информацию обо всех коммандах.',
            'статус': 'ℹ статус (<ответ на сообщение или @упоминание>) - выдает твой или чужой статус.',
            'имя': 'ℹ имя <текст длиной от 3 до 40 символов> - изменяет твой никнейм.',
            'роль': 'ℹ роль <текст длиной от 3 до 40 символов> - изменяет твою роль.',
            'пара': 'ℹ пара (фото) (<ответ на сообщение или @упоминание>) - шипперит двух людей.',
            'гиф': 'ℹ гиф <тег+гифки, слова разделяются плюсом> (<число от 1 до 100, кол-во вариаций>) - присылает гифку.',
            'семья': 'ℹ семья - выдает информацию о семье, ищет семью или взаимодействует с ней.',
            'рп': 'ℹ рп (*) <текст> - отправляет текст в формате ролевой игры.'
        }


    def echo(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        if self.chat:
            vk.messages.send(
                chat_id = kwargs['peer'] if 'peer' in kwargs else self.chat,
                message = ''.join(args) if all([True if str(i) == i else False for i in args]) else args,
                attachment = kwargs['attach'] if 'attach' in kwargs else '',
                keyboard = kwargs['keyboard'] if 'keyboard' in kwargs else {},
                random_id = 0)   
        else:
            vk.messages.send(
                peer_id = kwargs['peer'] if 'peer' in kwargs else self.peer,
                message = ''.join(args) if all([True if str(i) == i else False for i in args]) else args,
                attachment = kwargs['attach'] if 'attach' in kwargs else '',
                keyboard = kwargs['keyboard'] if 'keyboard' in kwargs else {},
                random_id = 0)   


    def handle(self, msg):
        # <cmd> <args, key=' '>

        if msg[:26] == '[club187703257|@asurachat]':
            msg = msg[26:].strip()
            if msg[0] == ',':
                msg = msg[1:].strip()
        elif msg[:21] == '[club187703257|Asura]':
            msg = msg[21:].strip()
            if msg[0] == ',':
                msg = msg[1:].strip()
        print(msg)

        if msg == 'Сбросить ник':
            self.handle('никнейм -')
        elif msg == 'Сбросить роль':
            self.handle('роль -')
        elif msg == 'Найти':
            self.handle('семья топ')
        elif msg == 'Моя семья':
            self.handle('семья инфо')
        elif msg == 'Выйти':
            self.handle('семья выйти')
        elif msg == 'Удалить':
            self.handle('семья удалить')
        elif msg == 'Принять Ислам':
            return self.echo(f'✅ {self.namel}, ты успешно принял Ислам!')

        cmd, args, argl = [], [], ''
        msg_splitted = msg.split(' ', 1)
        cmd = msg_splitted[0].lower()
        if len(msg_splitted) > 1:
            args = msg_splitted[1].split()
            argl = msg_splitted[1]
        if cmd in self.cmdsinfo.keys():
            updateStats(self.id, 'cmds_called', 1)
            print(f'\n"{msg}" handle-s:', str(datetime.now())[:-4])
            print({'cmd': cmd, 'args': args, 'argl': argl})
        
        if cmd == 'асура':
            if not argl:
                forms = [
                    'Ась?',
                    f'Слушаю тебя, {self.namel}!',
                    f'Да, {self.namel}?',
                    f'Доброго, {self.namel}!',
                    'М-м?'
                ]
                self.echo(choice(forms))
            if ' или ' in argl:
                m = choice(parsementions(argl).split(' или '))
                m = m[0].lower() + m[1:]
                for s in m:
                    if s in '?!.,;:':
                        m.replace(s, '')
                forms = [
                    f'{self.namel}, я думаю, что {m}.',
                    f'{self.namel}, я не уверена, но мне кажется {m}...'
                    f'{self.namel}, конечно {m}!'
                ]
                self.echo(choice(forms))

        if cmd == 'рп':
            if not argl:
                self.echo(
                    'ℹ рп <текст> - отправляет текст в формате ролевой игры.',
                    'ℹ рп * <текст> - отправляет действие в формате ролевой игры.'
                )
            else:
                t = None
                if args[0] == '*':
                    if len(args) > 1:
                        t = '*'
                        text = argl.split(' ', 1)[1]
                        text = text.replace('"', '').replace("'", '').replace('*', '')
                        parsed = parsementions(text)
                        self.echo(f'{self.namel}: *{parsed}*')
                    else:
                        return self.echo(f'❗ {self.namel}, если вы выбрали "*", то действие нужно указать!')
                else:
                    argl = argl.replace('"', '').replace("'", '').replace('*', '')
                    self.echo(f'{self.namel}: "{parsementions(argl)}"')
                rp = openjson('rp.json')
                if str(self.id) not in rp:
                    rp[str(self.id)] = {
                        'replics': 0,
                        'actions': 0,
                        'lastreplic': '',
                        'lastaction': ''
                    }
                if t == '*':
                    rp[str(self.id)]['actions'] += 1
                    rp[str(self.id)]['lastaction'] = f'*{parsed}*'
                else:
                    rp[str(self.id)]['replics'] += 1
                    rp[str(self.id)]['lastreplic'] = f'"{argl}"'
                rewritejson('rp.json', rp)

        if cmd == 'имя':
            if argl:
                names = openjson('names.json')
                busy = False
                for v in names.values():
                    if v.lower() == argl.lower():
                        busy = True
                if not busy:
                    admiss = checkSpelling(argl)
                    for s in argl:
                        if s == '-':
                            if str(self.id) in names:
                                del names[str(self.id)]
                            rewritejson('names.json', names)
                            self.name = getName(self.id)
                            self.namel = getNamel(self.id)
                            return self.echo(f'✅️ Теперь я зову тебя {self.namel}!')
                    if admiss:
                        updateStats(self.id, 'nicknames_changed', 1)
                        names[str(self.id)] = argl
                        rewritejson('names.json', names)
                        self.name = getName(self.id)
                        self.namel = getNamel(self.id)
                        return self.echo(f'✅️ Теперь я зову тебя {self.namel}!')
                    else:
                        return self.echo(f'❗ {self.namel}, этот никнейм точно больше двух и меньше 40 символов?\nТакже напоминаю, что никнеймы состоят только из букв и пробелов!')
                else:
                    return self.echo(f'❗ {self.namel}, такой никнейм уже занят!')
            self.echo(self.cmdsinfo['ник'])
        
        if cmd == 'роль':
            if argl:
                roles = openjson('roles.json')
                admiss = checkSpelling(argl)
                for s in argl:
                    if s == '-':
                        if str(self.id) in roles:
                            del roles[str(self.id)]
                        rewritejson('roles.json', str(roles).replace("'", '"'))
                        self.name = getName(self.id)
                        self.namel = getNamel(self.id)
                        return self.echo(f'✅️ Теперь я зову тебя {self.namel}!')
                if admiss:
                    updateStats(self.id, 'roles_changed', 1)
                    roles[str(self.id)] = argl
                    rewritejson('roles.json', str(roles).replace("'", '"'))
                    self.name = getName(self.id)
                    self.namel = getNamel(self.id)
                    return self.echo(f'✅ Теперь я зову тебя {self.namel}!')
                else:
                    return self.echo(f'❗ {self.namel}, эта роль точно больше двух и меньше 40 символов?\nТакже напоминаю, что роли состоят только из букв и пробелов!')
            self.echo(self.cmdsinfo['роль'])

        if cmd == 'пара':
            if self.peer == self.id:
                self.echo(f'❗ {self.namel}, такая команда работает только в беседах!')
            else:
                try:
                    people = vk.messages.getConversationMembers(peer_id = self.peer)['profiles']
                except Exception:
                    flag = False
                    return self.echo(f'❗ {self.namel}, такая команда работает только с правами администратора!')
                wp = False
                if self.reply:
                    t = self.reply['from_id']
                else:
                    t = choice(people)
                if argl:
                    if args[0] == 'фото':
                        wp = True
                    if ids(argl):
                        t = ids(argl)[0]
                t = t['id'] if type(t) == type({}) else t
                t = {
                    'id': t,
                    'name': getNamel(t),
                    'photo': getAvatar(t, self.peer) if wp else None
                }
                pt = choice(people)
                while pt['id'] == t['id']:
                    pt = choice(people)
                pt = {
                    'name': getNamel(pt['id']),
                    'photo':getAvatar(pt['id'], self.peer) if wp else None
                }
                mformatted = choice([
                    '❤ Думаю, что {} и {} - отличная пара!',
                    '💙 {}, тебе очень подходит {}, я уверена!',
                    '💛 Никто не знал, но {} и {} уже давно нравятся друг другу!'
                ]).format(t['name'], pt['name'])
                if t['photo']:
                    tp, ptp = f'{t["photo"]}', f'{pt["photo"]}'
                    return self.echo(mformatted, attach=(tp, ptp))
                else:
                    return self.echo(mformatted)
        
        if cmd == 'гиф':
            if not argl:
                return self.echo(self.cmdsinfo[2])
            c = None
            f = True
            if len(args) > 1:
                if not args[1].isdigit():
                    if not 1 <= int(args[1]) <= 100:
                        f = False
                else:
                    if 1 <= int(args[1]) <= 100:
                        c = int(args[1])
            if f:
                gif = getgif(
                    'https://api.giphy.com/v1/gifs/search?api_key=wZz52MVyc5G3r5CPKFYNgXl7vgIRwvzo&q=' + argl,
                    c if c else 10
                )
                if gif:
                    return self.echo(f'✅️ {self.namel}, гифка по запросу "{argl}":', attach=(uploadfile(gif, self.peer)))
                else:
                    return self.echo(f'❗ {self.namel}, гифок по запросу "{argl}" не оказалось!')
            else:
                self.echo(self.cmdsinfo['гиф'])

        if cmd == 'статус':
            flag = 1
            uid = self.id
            name = self.name
            if not argl:
                if self.reply:
                    flag = 0
                    uid = self.reply['from_id']
                    name = getName(uid)
            else:
                if ids(argl):
                    flag = 0
                    uid = ids(argl)[0]
                    name = getName(uid)
                else:
                    return self.echo(self.cmdsinfo['профиль'])
            if uid == self.id:
                flag = 1
            role = getRole(uid)
            rep = getRep(uid)
            stats = getStats(uid)
            family = getFamily(uid)
            rp = getRp(uid)
            form = [
                f'🙋‍ Твой никнейм - {name}, был изменен {stats["nicknames_changed"]} р.,',
                f'🎭 Твоя роль - {"пока неизвестна" if not role else role}, была изменена {stats["roles_changed"]} р.,',
                f'👪 Ты {"пока состоишь ни в одной семье" if not family else f"состоишь в семье {family}"},',
                f'💨 Твое последнее действие - {"пока неизвестно" if not rp["lastaction"] else rp["lastaction"]}, всего было {rp["actions"]} р.',
                f'🗣️ Твоя последняя реплика - {"пока неизвестна" if not rp["lastreplic"] else rp["lastreplic"]}, всего было {rp["replics"]} р.',
                f'🎩 Твоя репутация - {"пока неизвесна" if not rep else rep},',
                f'🤝🏻 Ты зауважал {stats["respected"]} ч.,',
                f'💬 Ты обращался к боту {stats["cmds_called"]} р.'
            ]
            form = '\n'.join(form)
            if flag:
                self.echo(
                    f'📒 Это профиль {self.namel}:\n\n {form}',
                    keyboard=keyboard(
                        [('Сбросить ник', 'secondary'), ('Сбросить роль', 'secondary')]
                    )
                )
            else:
                self.echo(f'📒 {self.namel}, это профиль {getNamel(uid)}:\n\n {form}')

        if cmd == 'помощь':
            if argl:
                if argl not in self.cmds:
                    self.echo(f'❗ {self.namel}, такой команды нет в списке команд! Если вы хотите узнать список команд, введите "помощь".')
                else:
                    self.echo(self.cmdsinfo[argl])
            else:
                form = ', '.join(list(self.cmdsinfo.keys()))
                self.echo(f'ℹ {self.namel}, вот все команды, на которые я могу отвечать:\n\n{form}')

        if cmd == 'семья':
            families = openjson('families.json')
            target = None
            act = None
            uid = None
            if argl:
                if ids(argl):
                    uid = ids(argl)[0]
                    for name, v in families.items():
                        if uid in v['members']:
                            target = name
                            break
                    if not target:
                        return self.echo(f'❗ {self.namel}, пользователь {getNamel(uid)} не вступил еще ни в одну беседу!')
                else:
                    if argl in families:
                        target = argl
                    else:
                        if args[0] == 'вступить':
                            if len(args) > 1:
                                target = argl.split(' ', 1)[1]
                            act = 'join'
                        elif args[0] == 'создать':
                            if len(args) > 1:
                                target = argl.split(' ', 1)[1]
                            act = 'add'
                        elif args[0] == 'описание':
                            if len(args) > 1:
                                text = argl.split(' ', 1)[1]
                            act = 'desc'
                        elif args[0] == 'название':
                            if len(args) > 1:
                                text = argl.split(' ', 1)[1]
                            act = 'name'
                        if args[0] == 'инфо':
                            act = 'info'
                            if self.reply:
                                uid = self.reply['from_id']
                                for name, v in families.items():
                                    if uid in v['members']:
                                        target = name
                                        break
                                if not target:
                                    return self.echo(f'❗ {self.namel}, пользователь {getNamel(uid)} не вступил еще ни в одну беседу!')    
                        elif args[0] == 'выйти':
                            act = 'leave'
                        elif args[0] == 'удалить':
                            act = 'rem'
                        elif args[0] == 'топ':
                            act = 'top'
            else:
                for k, v in families.items():
                    if self.id in v['members']:
                        target = k
                return self.echo(
                    f'ℹ семья создать <название> - создает семью, если ваша репутация больше 10.\n',
                    'ℹ семья вступить <название> - вступает в семью.\n',
                    keyboard=keyboard(
                        [('Найти', 'secondary'), ('Моя семья', 'secondary')]
                    )
                )
                target = None
            if target and target in families:
                family = families[target]
                fdesc = family['desc']
                fowner = family['owner']
                fmembers = family['members']
                fmembers_names = [getName(i) for i in fmembers]
                frep = family['rep']
                fdate = family['date']
                form = ',\n'.join([
                    f'{getNamel(fowner)}: "{fdesc}"',
                    f'Среди нас {", ".join(fmembers_names)}',
                    f'Общая репутация - {frep}',
                    f'Дата основания - {fdate}'
                ])
            if act == 'info':
                family = None
                for k, v in families.items():
                    if self.id in v['members']:
                        family = families[k]
                if not family:
                    return self.echo(
                        f'❗ {self.namel}, ты не являешься членом ни одной семьи! Если хочешь вступить в неё, можешь последовать приглашению друга или найти её!',
                        keyboard=keyboard(
                            [('Найти Семью', 'positive')]
                        )
                    )
                else:
                    fdesc = family['desc']
                    fowner = family['owner']
                    fmembers = family['members']
                    fmembers_names = [getName(i) for i in fmembers]
                    frep = family['rep']
                    fdate = family['date']
                    form = ',\n'.join([
                        f'{getNamel(fowner)}: "{fdesc}"',
                        f'Среди нас {", ".join(fmembers_names)}',
                        f'Общая репутация - {frep}',
                        f'Дата основания - {fdate}'
                    ])
                    if self.id != fowner:
                        return self.echo(
                            f'👪 {self.namel}, это информация о семье {k}:\n\n {form}',
                            keyboard=keyboard(
                                [('Выйти', 'negative')]
                            )
                        )
                    else:
                        return self.echo(
                            f'ℹ семья название <текст> - изменяет название семьи.\n',
                            'ℹ семья описание <текст> - изменяет описание семьи.\n\n',
                            f'👪 {self.namel}, это информация о семье {k}:\n\n {form}',
                            keyboard=keyboard(
                                [('Удалить', 'negative')]
                            )
                        )
            if act == 'join':
                if not target:
                    self.echo(f'❗ {self.namel}, выбери название семьи, в которую хочешь вступить!')
                else:
                    if self.id not in fmembers:
                        for name, v in families.items():
                            if self.id in v['members'] and k != target:
                                return self.echo(
                                    f'❗ {self.namel}, чтобы вступить в другую семью, для начала выйди из текущей!',
                                    keyboard=keyboard(
                                        [('Выйти', 'negative')]
                                    )
                                )
                        respects = openjson('respects.json')
                        if str(self.id) in respects:
                            families[target]['rep'] += 1
                        families[target]['members'] += [self.id]
                        rewritejson('families.json', families)
                        self.echo(f'✅ {self.namel}, ты успешно вступил в семью {target}!')
                    else:
                        self.echo(f'❗ {self.namel}, ты уже член этой семьи!')
            elif act == 'leave':
                for name, v in families.items():
                    if self.id in v['members']:
                        if self.id == v['owner']:
                            return self.echo(
                                f'❗ {self.namel}, ты не можешь выйти из семьи, если ты её создатель!\nЕсли ты хочешь избавиться от семьи, удали её.',
                                keyboard=keyboard(
                                    [('Удалить', 'negative')]
                                )
                            )
                        else:
                            families[target]['members'].remove(self.id)
                            return self.echo(f'✅ {self.namel}, ты успешно вышел из семьи {k}!')
                return self.echo(
                    f'{self.namel}, ты не являешься членом ни одной семьи! Если хочешь вступить в неё, можешь последовать приглашению друга, или ввести "семья топ".',

                )
            elif act == 'add':
                if not target:
                    self.echo(f'❗ {self.namel}, выбери название для семьи, которую хочешь основать!')
                else:
                    admiss = checkSpelling(target)
                    if not admiss:
                        return self.echo(f'❗ {self.namel}, это название точно больше двух и меньше 40 символов?\nТакже напоминаю, что названия состоят только из букв и пробелов!')
                    else:
                        if target in families:
                            return self.echo(f'❗ {self.namel}, семья с таким названием уже существует!')
                        else:
                            respects = openjson('respects.json')
                            if str(self.id) not in respects:
                                return self.echo(f'❗ {self.namel}, тебе не хватает репутации! Для основания семьи потребуется 5.')
                            else:
                                if len(respects[str(self.id)]) < 10:
                                    return self.echo(f'❗ {self.namel}, тебе не хватает репутации! Для основания семьи потребуется 5.')
                            if target in ['вступить', 'выйти', 'создать', 'удалить', 'топ', 'описание']:
                                return self.echo(f'❗ {self.namel}, некорректное название для семьи!')
                            families[target] = {
                                'desc': f'Добро пожаловать в семью {target}!',
                                'owner': self.id,
                                'members': [self.id],
                                'rep': len(respects[str(self.id)]),
                                'date': str(datetime.now())[:-7]
                            }
                            rewritejson('families.json', families)
                            self.echo(f'✅ {self.namel}, ты успешно основал семью {target}!')
            elif act == 'rem':
                for name, v in families.items():
                    if self.id == v['owner']:
                        del families[name]
                        rewritejson('families.json', families)
                        return self.echo(f'✅ {self.namel}, ты успешно удалил семью {name}! Все участники больше не имеют семью.')
                return self.echo(f'❗ {self.namel}, ты не являешься владельцем ни одной семьи!')
            elif act == 'desc':
                for k, v in families.items():
                    if self.id == v['owner']:
                        if not text:
                            self.echo(f'❗ {self.namel}, выбери новое описание для семьи!')
                        else:
                            families[k]['desc'] = text
                            rewritejson('families.json', families)
                            return self.echo(f'✅ {self.namel}, ты успешно изменил название семьи!')
                return self.echo(f'❗ {self.namel}, ты не являешься владельцем ни одной семьи!')
            elif act == 'name':
                for k, v in families.items():
                    if self.id == v['owner']:
                        if not text:
                            self.echo(f'❗ {self.namel}, выбери новое название для семьи!')
                        else:
                            admiss = checkSpelling(text)
                            if not admiss:
                                return self.echo(f'❗ {self.namel}, это название точно больше двух и меньше 40 символов?\nТакже напоминаю, что названия состоят только из букв и пробелов!')
                            else:
                                if text in families:
                                    return self.echo(f'❗ {self.namel}, семья с таким названием уже существует!')
                                else:
                                    copy = families[k]
                                    del families[k]
                                    families[text] = copy
                                    rewritejson('families.json', families)
                                    return self.echo(f'✅ {self.namel}, ты успешно изменил название семьи!')
                return self.echo(f'❗ {self.namel}, ты не являешься владельцем ни одной семьи!')

            elif act == 'top':
                si = []
                count = 0
                for k, v in families.items():
                    if count < 10:
                        si.append({'name': k, 'rep': v['rep']})
                    count += 1
                si = sorted(si, key=lambda x: x['rep'])
                form = '\n'.join([f'{i + 1} - {si[i]["name"]} с репутацией {si[i]["rep"]}' for i in range(len(si))])
                if not form:
                    form = 'Упс... Не найдено не одной семьи. Но ты можешь основать её первым!'
                self.echo(f'🔥 {self.namel}, это топ семей по репутации:\n\n {form}')

        
        respectkeys = ['+', 'респект', 'уважаю']
        if any(k in msg.split()[0].lower() for k in respectkeys) and self.reply:
            user = self.reply['from_id']
            respects = getRep(user)
            family = getFamily(user)
            families = openjson('families.json')
            if self.id not in respects:
                respects[str(user)] += [self.id]
                rewritejson('respects.json', respects)
                if family:
                    families[family]['rep'] += 1
                    rewritejson('families.json', families)
                self.echo(f'🤝🏻 +rep от {self.namel}\n{getNamel(int(user))}, твоя репутация повысилась до {len(respects[user])}!')
       
        if self.id == 244494455:
            if cmd == 'py3':
                self.echo(eval(argl))
            if cmd == 'debug':
                self.echo(parsementions(argl))
            if cmd == 'viewarea':
                self.echo(f'bot_script.py viewarea:\n{self.id}\n{self.name}\n{cmd}\n{args}')
            if cmd == 'echo':
                eval('self.echo(' + argl + ')')
        
        if cmd in self.cmdsinfo.keys():
            print(f'"{msg}" handle-e:', str(datetime.now())[:-7])


print('INIT FINISHED')


class mainThread(VkBotLongPoll):
    def listen(self):
        while True:
            try:                
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)


for event in mainThread(bot_session, 187703257).listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        e = event.obj
        etext = e['text']
        epeer = e['peer_id']
        echat = None
        if event.from_chat:
            echat = int(event.chat_id)
        efrom = e['from_id']
        reply = None
        if e['fwd_messages']:
            reply = e['fwd_messages'][0]
        else:
            if 'reply_message' in e:
                reply = e['reply_message']  
        if efrom > 0:
            if etext:
                if etext == 'sd' and efrom == 244494455:
                    Bot(efrom, epeer, echat, reply).echo('shutdowned at ' + str(datetime.now())[:-4])
                    exit()
                else:
                    bot = Bot(efrom, epeer, echat, reply)
                    Thread(target=bot.handle, args=(etext,)).start()