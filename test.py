import random
import socket
import threading
import json
import pymysql  # Импорт библиотек


from config import host, port, bd_name, bd_password, bd_user


def new_user(nickname):
    con = pymysql.connect(host=host, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    stats = {}
    for i in range(1, 11):
        stats.update({str(i): random.triangular(15, 25)//1})
    cur.execute(
        "UPDATE `user` SET `exp`='{}',`user_stats`='{}',`user_inventory`='{}',`user_equip`='{}',`location`='{}' "
        "WHERE `login`='{}'".format(0, json.dumps(stats), json.dumps([]), json.dumps({}), 1, nickname))
    con.commit()


def get_user_stats(nickname):
    con = pymysql.connect(host=host, user=bd_user, password=bd_password, database=bd_name)
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


def get_info(nickname):
    con = pymysql.connect(host=host, user=bd_user, password=bd_password, database=bd_name)
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


def bd_content(object_type, object_name, main_stats, min_main, max_main, min_extra, max_extra):
    con = pymysql.connect(host=host, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    for i in range(min_main, max_main+1):
        for j in range(1, 11):
            for k in range(min_extra, max_extra+1):
                cur.execute('INSERT INTO `object`(`name`, `object_type`, `main_stats_type`, `main_stats_value`, '
                            '`extra_stats_type`, `extra_stats_value`) VALUES '
                            '("{}","{}","{}","{}","{}","{}")'.format(object_name, object_type, main_stats, i, j, k))
    con.commit()


print(get_info("Login"))
