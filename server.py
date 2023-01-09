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


def broadcast(message):  # Функция связи
    for client in client_names.values():
        client.send(json.dumps({'command': 'message', 'content': '{}'.format(message)}).encode('utf-8'))


def registration(nickname, password):
    con = pymysql.connect(host=host_mysql, user=bd_user, password=bd_password, database=bd_name)
    cur = con.cursor()
    cur.execute("INSERT INTO `user` (`Login`, `P@ssword`) VALUES " + '("{}", "{}")'.format(nickname, password))
    con.commit()


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
                                client.send('User already in chat'.encode('utf-8'))
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

    client_names.update({nickname: client})
    print("User name {}".format(nickname))
    broadcast("{} connected!".format(nickname))

    while True:
        try:  # Получение сообщений от клиента
            message = json.loads(client.recv(8192).decode('utf-8'))
            match message['command']:
                case 'message':
                    broadcast(message['content'])
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
