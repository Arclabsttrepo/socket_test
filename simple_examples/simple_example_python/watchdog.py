#!/usr/bin/env python3

#The watchdog/server script that handles passing messages between clients using JSON strings.

from platform import node
import socket
import threading
import conversion
import pdb
import subprocess

# define constants:
HEADER_SIZE = 64
PORT = 5050 #The port the server and all clients are connected to.
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

# Creates the server socket with the domain as IPv4 protocol
# and the type as TCP/IP.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Binds the server to the address and port specified in ADDR constant.
server.bind(ADDR)

# Converts the message to a JSON string, encodes the message, gets 
# message length and creates the HEADER message and sends the HEADER
# message and actual message to the client.
def Send_string_to_client(sent_from_node, conn, msg):
    try:
        # Converts the messafe to a JSON string using a conversion library.
        msg_json_string = conversion.Conversion_To_Json(sent_from_node,msg)
        # Encodes the message in UTF-8 format.
        message_utf = msg_json_string.encode(FORMAT)
        # Creates the HEADER message to be sent by encoding the message
        # length as a string in UTF-8 format and packing the HEADER with
        # blank spaces (in UTF-8 notation) to fill the HEADER message with
        # the no. of bytes the client expects to receive (i.e HEADER_SIZE).
        msg_length = len(message_utf)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER_SIZE - len(send_length))
        # Sends the HEADER message to the client.
        conn.send(send_length)
        # Sends the actual message to the client.
        conn.send(message_utf)
        print("[SENDING TO CLIENT] " + str(msg))
    except:
        print("ERROR!")

# Receives and decodes the messages recevied from the client.
def Receive_string_from_client(conn):
    # Receives and decodes the HEADER message from the client.
    # The number of bytes to be received is set as HEADER_SIZE.
    received_msg_length = conn.recv(HEADER_SIZE).decode(FORMAT)
    # If the HEADER message is received, then convert the HEADER message
    # to an integer, receive and decode the actual message from the client
    # with the no. of bytes to be received set as the integer defined 
    # in the HEADER message.
    if received_msg_length:
        received_msg_length = int(received_msg_length)
        received_msg = conn.recv(received_msg_length).decode(FORMAT)
        print("[CLIENT SAID] " + str(received_msg))
        # Converts the message received to a python Dictionary.
        received_msg_dict=conversion.Json_To_Dict(received_msg)
        return received_msg_dict
    # If no HEADER message is received close the connection. 
    else:
        return "other connection closed"

# Sends messages from one client to another using the server.
def Push(conn, msg, node_name):
    try:
        # Lock so no other threads can access these sockets
        lock.acquire()   
        # Store the name of the node being sent to and the message.
        node_to_send_msg_to = msg['key']
        msg_to_send_to_node = msg['msg']
        # This checks that node_to_send_to exists in the dictionary. 
        # That means that the node is alive and connected. 
        # Else KeyError is raised.
        node_to_send_to_socket_object = nodes[node_to_send_msg_to]
        # Sends message to client.
        Send_string_to_client(node_name, node_to_send_to_socket_object, msg_to_send_to_node)
        # unlock so other threads can access these sockets
        lock.release()
    except KeyError:
        # If node not registered with watchdog, this error is thrown.
        # Unlock so other threads can access these sockets
        lock.release()
        print(str(node_to_send_msg_to)+" not connected")

        #######################################################
        '''
        FOR FUTURE:
         if node not found in dictionary
         print("Node not found in registered nodes list!")
         so that node that tried to push can take some action
         knowing that no data was sent to the requested node
         #Send_string_to_client(conn, "Node not found in registered nodes list!")
        '''
        ######################################################



# Receives messages from the client after registering with the server.
def Handle_client(conn, addr, node_name):
    print(f"[NEW CONNECTION] {addr}  {node_name} connected.")
    connected = True
    try:
        while connected:
            msg = Receive_string_from_client(conn)
            # If the disconnect from watchdog message is received from client
            # Then deregister node from nodes dictionary and close connection.
            if msg['key'] == "watchdog" and msg['msg'] == DISCONNECT_MESSAGE:
                print(f"{node_name} has disconnected.")
                nodes.pop(node_name)
                connected = False
            # If the message is not for the watchdog then send to the specified client.    
            if msg['key'] != "watchdog":
                Push(conn, msg, node_name)
        conn.close()
        print(f"[CLOSING THREAD]")
    except ConnectionResetError:
        print(f"Connection to {node_name} lost!")
        #Deregister node from nodes list when connection is lost.
        nodes.pop(node_name)
        conn.close()
        print(f"[CLOSING THREAD]")


# The server listens for connections, then accepts when a connection is established,
# and creates a separate thread to handle each client.
def Start_server():
     #The server listens for incoming connections from clients.
    server.listen()
    
    ###############################################################
    #for launching scripts in  the future
    #subprocess.call(['gnome-terminal', '-e', 'python3 client1.py'])
    #subprocess.call(['gnome-terminal', '-e', 'python3 client2.py'])
    ################################################################

    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # Accepts a client's connection to the server. 
        # It blocks the execution of
        # processes until the connection is established
        conn, addr = server.accept()
        # Stores the message received in a temporary variable.
        client_name = Receive_string_from_client(conn)       
        # If a message is received from the client to the watchdog.
        # then attempt to register the node.
        if client_name and client_name['key'] == "watchdog":
            # Ensures only this thread can access nodes.
            lock.acquire()
            # Register the node name in the node dictionary
            node_name = client_name['msg']
            # key = node_name
            # value = conn
            # If node already exists then close client connection.
            if node_name in nodes:
                print(f"{node_name} already registered! Closing connection!")
                conn.close()
                #Allows other threads to access the nodes dictionary.
                lock.release()
            # If node does not exist then update nodes dictionary with client name and client object.    
            else:
                nodes.update({node_name: conn})
                # Allows other threads to access the nodes dictionary.
                lock.release()
                # create a new thread to handle the new connection
                thread = threading.Thread(target=Handle_client, args=(conn, addr, node_name))
                thread.start()

                print(f"[ACTIVE CONNETIONS] {threading.active_count() - 1}")
        else:
            print("[NODE DID NOT REGISTER] Awaiting new connections.")

# Main code execution
print("[STARTING SERVER]")
try:
    Start_server()
except KeyboardInterrupt:
    print("[SHUTTING DOWN SERVER]")
