import socket
import sys
import threading

host = 'localhost'
port = 5555

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


try:
    clientsocket.connect((host, port))
except socket.error as e:
    print(e)


def listen(s):
    while True:
        msg = s.recv(1024)
        print('\r\r' + msg.decode('utf-8') + '\n' + f'you: ', end='')


threading.Thread(target=listen, args=(clientsocket, ), daemon=True).start()
clientsocket.send(str.encode('join'))


while True:
    message = input('you: ')
    clientsocket.send(str.encode(message))
