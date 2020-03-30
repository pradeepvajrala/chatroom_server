import socket
import select
import os

HEADER_LENGTH = 10
IP= '127.0.0.1'
PORT= 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list=[server_socket]

clients ={}

def message_receive(socket_client):
    try:
        message_header = socket_client.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header" : message_header, "data" : socket_client.recv(message_length)}
    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    
    for notified_sockets in server_socket:
        if notified_sockets == server_socket:
            socket_client, client_address = server_socket.accept()
            user = message_receive(socket_client)
            if user is False:
                continue
            sockets_list.append(socket_client)
            clients[socket_client] = user
            print(f"Accepted new request from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
        
        else:
            message = message_receive(notified_sockets)
            if message is False:
                print("Connection is closed from{clients[notified_sockets]['data'].decode('utf-8')}")
                sockets_list.remove(notified_sockets)
                del clients[notified_sockets]
                continue

            user = clients[notified_sockets]
            print(f"Received message from {user['data'.decode('utf-8')]}: {message['data'].decode('utf-8')}")

            for socket_client in clients:
                if socket_client != notified_sockets:
                    socket_client.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_sockets in exception_sockets:
        sockets_list.remove(notified_sockets)
        del clients[notified_sockets]