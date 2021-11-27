import socket
import sys
import threading
from _thread import start_new_thread

host = 'localhost'
port = 5555


serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversocket.bind((host, port))
# serversocket.listen(2)

print('server is running')


def get_index(addr, members):
    for i in range(len(members)):
        if addr == members[i]:
            return i


members = []
while True:
    msg, addr = serversocket.recvfrom(1024)

    if addr not in members and len(members) <= 100:
        members.append(addr)

    print(f'New connection established: {addr}')

    client_id = addr[1]
    if msg.decode('utf-8') == 'join':
        print(f'client {client_id} joined chat')

    if msg.decode('utf-8') == 'exit':
        i = get_index(addr, members)
        mes = 'Собеседник вышел из чата'
        addr_pop = []
        if i % 2 == 0:
            addr_pop = members[i+1]
            members.pop(i+1)
            members.pop(i)
            serversocket.sendto(str.encode(mes), addr_pop)
        else:
            addr_pop = members[i-1]
            members.pop(i)
            members.pop(i-1)
            serversocket.sendto(str.encode(mes), addr_pop)
        continue

    if msg.decode('utf-8') != 'join':
        i = get_index(addr, members)
        if i % 2 == 0:
            try:
                if not msg:
                    continue
                msg = f'client {client_id}: {msg.decode("utf-8")}'
                serversocket.sendto(str.encode(msg), members[i+1])
            except IndexError:
                mes = 'Подождите подключения собеседника'
                serversocket.sendto(str.encode(mes), members[i])
                continue
        else:
            if not msg:
                continue
            msg = f'client {client_id}: {msg.decode("utf-8")}'
            serversocket.sendto(str.encode(msg), members[i-1])

