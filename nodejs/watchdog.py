#!/usr/bin/env python3
# server

from platform import node
import socket
import threading
import conversion
import pdb
import subprocess
import time

# define constants:
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

#address and port to send data to nodejs
PORT2 = 5051
SERVER2 = '127.0.0.1'
ADDR2 = (SERVER2, PORT2)

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

# create client socket object for nodejs
client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client2.connect(ADDR2)


def Send_string_to_client(sent_from_node, conn, msg):
    
    msg_json_string = conversion.Conversion_To_Json(sent_from_node,msg)
    message_utf = msg_json_string.encode(FORMAT)
    msg_length = len(message_utf)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message_utf)
    print("[SENDING TO CLIENT] " + str(msg))


def Receive_string_from_client(conn):
    
    received_msg_length = conn.recv(HEADER).decode(FORMAT)
    # in the event that the socket sends something blank:
   
    if received_msg_length:
        received_msg_length = int(received_msg_length)
        received_msg = conn.recv(received_msg_length).decode(FORMAT)
        print("[CLIENT SAID] " + str(received_msg))
        received_msg_dict=conversion.Json_To_Dict(received_msg)
        return received_msg_dict
    else:
        return "other connection closed"


def Push(conn, msg, node_name):
    try:
        # lock so no other threads can access these sockets
        lock.acquire()
        
        #store the name of the node being sent to and the message
        node_to_send_msg_to = msg['key']
        msg_to_send_to_node = msg['msg']
        

        #This also checks that node_to_send_to exists in the dictionary. That means that the node is alive and connected. Else KeyError is raised.
        node_to_send_to_socket_object=nodes[node_to_send_msg_to]
        Send_string_to_client(node_name, node_to_send_to_socket_object, msg_to_send_to_node)

        # unlock so other threads can access these sockets
        lock.release()
    except KeyError:
        #if node not registered with watchdog, this error is thrown
        # unlock so other threads can access these sockets
        lock.release()
        print(str(node_to_send_msg_to)+" not connected")

        '''
        FOR FUTURE:
         if node not found in dictionary
         print("Node not found in registered nodes list!")
         so that node that tried to push can take some action
         knowing that no data was sent to the requested node
         #Send_string_to_client(conn, "Node not found in registered nodes list!")
        '''




def Handle_client(conn, addr, node_name):
    print(f"[NEW CONNECTION] {addr}  {node_name} connected.")
    connected = True

    try:
        while connected:
            msg = Receive_string_from_client(conn)
            if msg['key'] == "watchdog" and msg['msg'] == DISCONNECT_MESSAGE:
                print(f"{node_name} has disconnected.")
                nodes.pop(node_name)
                connected = False

            #print(f"[{node_name}] says: {msg}")

            if msg['key'] != "watchdog":
                Push(conn, msg, node_name)


        conn.close()
        print(f"[CLOSING THREAD]")
    except ConnectionResetError:
        print(f"Connection to {node_name} lost!")


def Start_server():
    server.listen()
   
    #subprocess.call(['gnome-terminal', '-e', 'python3 client1.py'])
    #subprocess.call(['gnome-terminal', '-e', 'python3 client2.py'])

    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # wait for new connetion from client
        conn, addr = server.accept()

        temp_return = Receive_string_from_client(conn)
        

        
        # register the node name in the node dictionary
        if temp_return and temp_return['key'] == "watchdog":
            node_name = temp_return['msg']
            # key=node_name
            # value=conn

            #check if node already exists:
            lock.acquire()
            if node_name in nodes:
                print(f"{node_name} already registered! Closing connection!")
                conn.close()
                lock.release()
            else:
                nodes.update({node_name: conn})
                lock.release()
                # create a new thread to handle the new connection
                thread = threading.Thread(target=Handle_client, args=(conn, addr, node_name))
                thread.start()

                print(f"[ACTIVE CONNETIONS] {threading.active_count() - 1}")
        else:
            print("[NODE DID NOT REGISTER] Awaiting new connections.")


print("[STARTING SERVER]")
try:
    #start send to nodejs
    var="test"
    var=var.encode(FORMAT)
    client2.send(var)
    time.sleep(1)
    #end send to nodejs

    Start_server()
except KeyboardInterrupt:
    print("[SHUTTING DOWN SERVER]")