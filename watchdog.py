#!/usr/bin/env python3
# server

from platform import node
import socket
import threading

# define constants:
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# dictionary for topics
topics = []
# dictionary for node names
nodes = {}

# lock for sharing variables between threads
lock = threading.Lock()

# topics are names for variables that are meant to be updated periodically
# many nodes can push to them and many nodes can pull from them
# although it makes more sense for one node to push to them while one or many
# nodes pull from them
# the value stored in a topic is the last one updated by the node that generates it
# nodes are individual scripts

# create server socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def Send_string_to_client(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)
    print("[SENDING TO CLIENT] " + msg)


def Receive_string_from_client(conn):
    loopUntilMessageReceived = True
    received_msg_length = conn.recv(HEADER).decode(FORMAT)
    # in the event that the socket sends something blank:
    while loopUntilMessageReceived:
        if received_msg_length:
            received_msg_length = int(received_msg_length)
            received_msg = conn.recv(received_msg_length).decode(FORMAT)
            print("[CLIENT SAID] " + received_msg)
            loopUntilMessageReceived = False
            return received_msg


def push(conn, msg, node_name):
    try:
        # try to access node from node list
        # lock so no other threads can access these sockets
        lock.acquire()
        node_to_send_to = "client2"
        #This also checks that node_to_send_to exists in the dictionary. That means that the node is alive and connected. Else KeyError is raised.
        node_to_send_to_socket_object=nodes[node_to_send_to]
        Send_string_to_client(node_to_send_to_socket_object, msg[5:])

        lock.release()
    except KeyError:
        lock.release()
        #FOR FUTURE:
        # if node not found in dictionary
        # print("Node not found in registered nodes list!")
        # so that node that tried to push can take some action
        # knowing that no data was sent to the requested node
        print(str(node_to_send_to)+" not connected")
        #Send_string_to_client(conn, "Node not found in registered nodes list!")




def Handle_client(conn, addr, node_name):
    print(f"[NEW CONNECTION] {addr}  {node_name} connected.")
    connected = True

    try:
        while connected:
            # conn.send("connection_successful".encode(FORMAT))
            msg = Receive_string_from_client(conn)
            # msg = conn.recv(HEADER).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                print(f"{node_name} has disconnected.")
                connected = False

            print(f"[{node_name}] says: {msg}")
            # print(f"[{addr}] {msg}")



            if msg[0:5] == "push:":
                push(conn, msg, node_name)


        conn.close()
        print(f"[CLOSING THREAD]")
    except ConnectionResetError:
        print(f"Connection to {node_name} lost!")


def Start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # wait for new connetion from client
        conn, addr = server.accept()

        temp_return = Receive_string_from_client(conn)
        # temp_return = conn.recv(HEADER).decode(FORMAT)

        # register the node name in the node dictionary
        if temp_return and temp_return[0:5] == "name:":
            node_name = temp_return[5:]
            # key=node_name
            # value=conn
            nodes.update({node_name: conn})

            # create a new thread to handle the new connection
            thread = threading.Thread(target=Handle_client, args=(conn, addr, node_name))
            thread.start()

            print(f"[ACTIVE CONNETIONS] {threading.active_count() - 1}")
        else:
            print("[NODE DID NOT REGISTER] Awaiting new connections.")


print("[STARTING SERVER]")
try:
    Start_server()
except KeyboardInterrupt:
    print("[SHUTTING DOWN SERVER]")
