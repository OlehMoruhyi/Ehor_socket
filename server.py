# server.py
import socket
import threading
import json
import pymysql  # Импорт библиотек
import random

from config import host, port, bd_name, bd_password, bd_user, host_mysql


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Инициализация сокета
server.bind((host, port))  # Назначение хоста и порта к сокету
server.listen()

client_names = {}


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def monster_fight(nickname, beast_location, beast_level, beast_type):
    beast_stats = {}
    for i in range(1, 11):
        beast_stats.update({str(i): random.triangular(10 + beast_level * 2 / 3,
                                                      15 + beast_level * 1.2 + random.triangular(beast_type,
                                                                                                 beast_type * 3)) // 1})

    beast_stats.update({str(beast_location * 2 - 1): beast_stats[str(beast_location * 2 - 1)] + random.triangular(
        beast_type * 3 + beast_level / 2, beast_type * 4 + beast_type * beast_type + beast_level * 2) // 1})
    beast_stats.update({str(beast_location * 2): beast_stats[str(beast_location * 2)] + random.triangular(
        beast_type * 3 + beast_level / 2, beast_type * 4 + beast_type * beast_type + beast_level * 2) // 1})
    user_stats = get_user_stats(nickname)
    match fight(beast_stats, user_stats):
        case 0:
            client_names[nickname].send(json.dumps(
                {'command': 'only_user_message', 'content': "No peace way"}).encode('utf-8'))
        case 1:
            new_user(nickname)
            client_names[nickname].send(json.dumps(
                {'command': 'only_user_message', 'content': "You dead"}).encode('utf-8'))

        case 2:

            con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
            cur = con.cursor()
            cur.execute("SELECT `exp` FROM `user` WHERE `login`='{}'".format(nickname))
            exp = cur.fetchone()[0] + 1.2 ** beast_level * 100 // 1
            cur.execute("UPDATE `user` SET `exp`='{}' WHERE `login`='{}'".format(exp, nickname))
            con.commit()
            for i in range(beast_type):
                cur.execute("SELECT `id` FROM `object` WHERE `main_stats_type`='{}' ORDER BY RAND () LIMIT 1".
                            format(random.choice([beast_location * 2 - 1, beast_location * 2])))

                add_to_inventory(nickname, cur.fetchone()[0], beast_level)
            client_names[nickname].send(json.dumps(
                {'command': 'only_user_message', 'content': "You win"}).encode('utf-8'))


def fight(stats_1, stats_2):
    hp_1 = stats_1["1"] * 10
    attack_1 = - stats_2["2"]/3
    attack_1 += (stats_1["3"] - stats_2["4"], 0)[(stats_1["3"] - stats_2["4"]) < 0]
    attack_1 += (stats_1["5"] - stats_2["6"], 0)[(stats_1["5"] - stats_2["6"]) < 0]
    attack_1 += (stats_1["7"] - stats_2["8"], 0)[(stats_1["7"] - stats_2["8"]) < 0]
    attack_1 += (stats_1["9"] - stats_2["10"], 0)[(stats_1["9"] - stats_2["10"]) < 0]
    hp_2 = stats_2["1"] * 10
    attack_2 = - stats_1["2"]/3
    attack_2 += (stats_2["3"] - stats_1["4"], 0)[(stats_2["3"] - stats_1["4"]) < 0]
    attack_2 += (stats_2["5"] - stats_1["6"], 0)[(stats_2["5"] - stats_1["6"]) < 0]
    attack_2 += (stats_2["7"] - stats_1["8"], 0)[(stats_2["7"] - stats_1["8"]) < 0]
    attack_2 += (stats_2["9"] - stats_1["10"], 0)[(stats_2["9"] - stats_1["10"]) < 0]
    while True:
        if attack_2 <= 0 and attack_1 <= 0:
            return 0
        hp_2 -= attack_1
        hp_1 -= attack_2
        if hp_1 <= 0:
            return 2
        if hp_2 <= 0:
            return 1


def duel(nickname_1, nickname_2):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    match fight(get_user_stats(nickname_1), get_user_stats(nickname_2)):
        case 0:
            client_names[nickname_1].send(json.dumps(
                {'command': 'only_user_message', 'content': "Only peace way in duel between " + nickname_1 + " and "
                                                            + nickname_2}).encode('utf-8'))
            if nickname_2 in client_names.keys():
                client_names[nickname_2].send(json.dumps(
                    {'command': 'only_user_message', 'content': "Only peace way in duel between " + nickname_1 + " and "
                                                                + nickname_2}).encode('utf-8'))
        case 1:
            new_user(nickname_2)
            cur.execute("SELECT `player_kill` FROM `user` WHERE `login`='{}'".format(nickname_1))
            player_kill = cur.fetchone()[0] + 1
            cur.execute("UPDATE `user` SET `player_kill`='{}' WHERE `login`='{}'".format(player_kill, nickname_1))
            client_names[nickname_1].send(json.dumps(
                {'command': 'only_user_message', 'content': nickname_1 + " kills " + nickname_2}).encode('utf-8'))
            if nickname_2 in client_names.keys():
                client_names[nickname_2].send(json.dumps(
                    {'command': 'only_user_message', 'content': nickname_1 + " kills " + nickname_2}).encode('utf-8'))
        case 2:
            new_user(nickname_1)
            cur.execute("SELECT `player_kill` FROM `user` WHERE `login`='{}'".format(nickname_2))
            player_kill = cur.fetchone()[0] + 1
            cur.execute("UPDATE `user` SET `player_kill`='{}' WHERE `login`='{}'".format(player_kill, nickname_2))
            client_names[nickname_1].send(json.dumps(
                {'command': 'only_user_message', 'content': nickname_2 + " kills " + nickname_1}).encode('utf-8'))
            if nickname_2 in client_names.keys():
                client_names[nickname_2].send(json.dumps(
                    {'command': 'only_user_message', 'content': nickname_2 + " kills " + nickname_1}).encode('utf-8'))


def new_user(nickname):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    stats = {}
    for i in range(1, 11):
        stats.update({str(i): random.triangular(15, 25)//1})
    cur.execute(
        "UPDATE `user` SET `exp`='{}',`user_stats`='{}',`user_inventory`='{}',`user_equip`='{}',`location`='{}' "
        "WHERE `login`='{}'".format(0, json.dumps(stats), json.dumps([]), json.dumps({}), random.triangular(1, 5)//1,
                                    nickname))
    con.commit()


def get_info(nickname):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()

    cur.execute("SELECT `user_inventory`, `exp`, `location` FROM `user` WHERE `login` = '{}'".format(nickname))
    pre_info = cur.fetchone()
    level = (pre_info[1]/100)**(2/3)//1
    pre_inventory_info = json.loads(pre_info[0])
    inventory_info = []
    for i in pre_inventory_info:
        cur.execute("SELECT `name` FROM `object` WHERE `id` = '{}'".format(i.get("object_id")))
        inventory_info.append({"name": cur.fetchone()[0], "level": i.get("level")})

    pre_stats = list(get_user_stats(nickname).values())
    stats_name = ["Health", "Heal", "Fire_attack", "Fire_resist", "Air_attack", "Air_resist", "Water_attack",
                  "Water_resist", "Earth_attack", "Earth_resist"]
    stats = ""
    for i in range(5):
        stats += "{:14}: {:<10} {:14}: {:<10}\n"\
            .format(stats_name[2*i], pre_stats[2*i], stats_name[2*i+1], pre_stats[2*i+1])

    info = {"command": "info", "stats": stats, "inventory": inventory_info,
            "level": level, "location": pre_info[2],
            "beasts": [random.choice([1, 2, 3]), random.choice([1, 2, 3]), random.choice([1, 2, 3])]}

    cur.execute("SELECT `login` FROM `user` WHERE `location`='{}' AND `login` != '{}' ORDER BY RAND () LIMIT 2".
                format(info["location"], nickname))
    pre_duels = cur.fetchall()
    duels = []
    for i in pre_duels:
        duels.append(i[0])
    info.update({"duels": duels})
    return info


def broadcast(message):  # Функция связи
    for client in client_names.values():
        client.send(json.dumps({'command': 'message', 'content': '{}'.format(message)}).encode('utf-8'))


def registration(nickname, password):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    cur.execute("INSERT INTO `user` (`Login`, `P@ssword`) VALUES " + '("{}", "{}")'.format(nickname, password))
    con.commit()
    new_user(nickname)


def add_to_inventory(nickname, object_id, level):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    cur.execute("SELECT `object_type` FROM `object` WHERE `id`='{}'".format(object_id))
    object_type = cur.fetchone()
    cur.execute("SELECT `user_inventory` FROM `user` WHERE `login`='{}'".format(nickname))
    user_inventory = cur.fetchone()
    if object_type and user_inventory:
        if user_inventory[0]:
            user_inventory = json.loads(user_inventory[0])
        else:
            user_inventory = []
        user_inventory = [{"object_type": object_type[0], "object_id": object_id, "level": level}] + user_inventory
        while True:
            if len(user_inventory) > 25:
                user_inventory.pop(25)
            else:
                break
        cur.execute("UPDATE `user` SET `user_inventory`='{}' WHERE `login`='{}'".format(json.dumps(user_inventory),
                                                                                            nickname))
        con.commit()


def equip(nickname, inventory_id):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    cur.execute("SELECT `user_inventory` FROM `user` WHERE `login`='{}'".format(nickname))

    object_info = cur.fetchone()
    if object_info:
        try:
            if object_info[0]:
                object_info = json.loads(object_info[0])[inventory_id]
            object_type = object_info['object_type']
            object_id = object_info['object_id']
            level = object_info['level']
            cur.execute("SELECT `user_equip` FROM `user` WHERE `login`='{}'".format(nickname))
            user_equip = cur.fetchone()
            if user_equip:
                if user_equip[0]:
                    user_equip = json.loads(user_equip[0])
                else:
                    user_equip = {}
                user_equip.update({object_type: {"object_id": object_id, "level": level}})
                cur.execute("UPDATE `user` SET `user_equip`='{}' WHERE `login`='{}'".format(json.dumps(user_equip),
                                                                                            nickname))
                con.commit()
        except IndexError as e:
            print(e)


def go(nickname, location):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    cur.execute("UPDATE `user` SET `location`='{}' WHERE `login`='{}'".format(location, nickname))
    con.commit()
    client_names[nickname].send(json.dumps({'command': 'only_user_message', 'content': 'Go to the location {}'.
                                           format(location)}).encode('utf-8'))


def get_user_stats(nickname):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    cur.execute("SELECT `user_stats` FROM `user` WHERE `login`='{}'".format(nickname))
    user_stats = cur.fetchone()
    if user_stats and user_stats[0]:
        user_stats = json.loads(user_stats[0])
    elif user_stats:
        new_user(nickname)
        cur.execute("SELECT `user_stats` FROM `user` WHERE `login`='{}'".format(nickname))
        user_stats = cur.fetchone()
    else:
        user_stats = {}
        for i in range(1, 11):
            user_stats.update({str(i): 0})
    cur.execute("SELECT `user_equip` FROM `user` WHERE `login`='{}'".format(nickname))
    user_equip = cur.fetchone()
    if user_equip and user_equip[0]:
        for i in json.loads(user_equip[0]).values():
            cur.execute(
                "SELECT `main_stats_type`, `main_stats_value`, `extra_stats_type`, `extra_stats_value` FROM `object` WHERE `id`='{}'".format(
                    i.get("object_id", "0")))
            cur_equip = cur.fetchone()
            if cur_equip:
                user_stats.update({str(cur_equip[0]): user_stats.get(str(cur_equip[0]), 0) + cur_equip[1] + (
                        1.2 ** i.get("level")) // 1})
                user_stats.update({str(cur_equip[2]): user_stats.get(str(cur_equip[2]), 0) + cur_equip[3] + (
                        1.2 ** i.get("level")) // 1})
    return user_stats


def handle(client):
    while True:  # registration and verification
        try:  # get messages from clients
            message = json.loads(client.recv(8192).decode('utf-8'))
            print(message)
            if message['command'] == 'verification':
                try:
                    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
                    cur = con.cursor()
                    cur.execute("SELECT `P@ssword` FROM `user` WHERE `Login` = " + '"{}"'.format(message['login']))

                    row = cur.fetchone()
                    if row[0]:
                        if row[0] == message['p@ssword']:
                            if message['login'] in client_names.keys():
                                client.send('User already in game'.encode('utf-8'))
                            else:
                                nickname = message['login']
                                client.send('SUCCESS'.encode('utf-8'))
                                break
                        else:
                            client.send('Wrong password'.encode('utf-8'))
                    else:
                        client.send('This login does not registration'.encode('utf-8'))
                except pymysql.Error as e:  # unsuccessful verification
                    print(e.args[1])

            elif message['command'] == 'registration':
                try:
                    registration(message['login'], message['p@ssword'])
                    nickname = message['login']
                    client.send('SUCCESS'.encode('utf-8'))
                    break
                except pymysql.Error as e:  # unsuccessful registration
                    print(e.args[1])
                    client.send('This login already exists, enter unique login'.encode('utf-8'))

            else:
                client.send('Degan, this command does not not exist'.encode('utf-8'))
        except Exception as e:  # close client
            print(e)
            client.close()
            return None

    info = get_info(nickname)
    client_names.update({nickname: client})
    print("User name {}".format(nickname))
    broadcast("{} connected!".format(nickname))

    while True:
        try:  # Получение сообщений от клиента
            message = json.loads(client.recv(8192).decode('utf-8'))
            match message['command']:
                case 'message':
                    broadcast(message['content'])
                case 'equip':
                    equip(nickname, message['id'])
                    info = get_info(nickname)
                    client.send(json.dumps(info).encode('utf-8'))
                case 'fight':
                    monster_fight(nickname, info["location"], info["level"], info["beasts"][message['id']])
                case 'duel':
                    try:
                        duel(nickname, info["duels"][message['id']])
                    except IndexError as e:
                        info = get_info(nickname)
                        client.send(json.dumps(info).encode('utf-8'))
                case 'go':
                    go(nickname, message['id'])
                case 'get_info':
                    info = get_info(nickname)
                    client.send(json.dumps(info).encode('utf-8'))
                case 'close':
                    broadcast('{} left us!'.format(nickname))
                    client_names.pop(nickname)
                    client.close()
                    print('{} left us!'.format(nickname))
                    break
                case _:
                    broadcast('Degan, this command does not not exist')
        except Exception as e:  # Удаление клиентов
            try:
                print(e)
                broadcast('{} left us!'.format(nickname))
                client_names.pop(nickname)
                client.close()
                print('{} left us!'.format(nickname))
                break
            except Exception as e:
                print(e)
                client_names.pop(nickname)
                broadcast('{} left us!'.format(nickname))
                client.close()
                print('{} left us!'.format(nickname))
                break


def receive():  # Подключение нескольких клиентов
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
