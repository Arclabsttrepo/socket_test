#server
from platform import node
import socket
import threading

#define constants:
HEADER = 2048
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

#dictionary for topics
topics = []
#dictionary for node names
nodes = {}
#dictionary for nodes' incoming messages
nodes_messages ={}
#lock for sharing variables between threads
lock = threading.Lock()

#topics are names for variables that are meant to be updated periodically
#many nodes can push to them and many nodes can pull from them
#although it makes more sense for one node to push to them while one or many
#nodes pull from them
#the value stored in a topic is the last one updated by the node that generates it
#nodes are individual scripts 

#create server socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def push(conn, addr, msg, node_name):
        try:
            #try to access node from node list
            #lock so no other threads can access these sockets
            lock.acquire()
            node_to_send_to = msg[5:]
            node_to_send_to_socket_object=nodes[msg[5:]]
            #ensure node exits in both dictionarys:
            nodes_messages[node_to_send_to]
            #if no errors(node found):
            #tell reqesting node it is ready for the data:
            conn.send("node_found_push_the_data".encode(FORMAT))
            #add the name of the node who sent the data to the message
            #separate node name and message by a colon
            data_to_send = node_name+":"+conn.recv(HEADER).decode(FORMAT)
            #if the incoming messages for the node is blank, add the data
            if nodes_messages[msg[5:]] == " ":
                nodes_messages.update({node_to_send_to: data_to_send})
            else:
                #if other nodes wrote to the dictionary for this node
                #add on the new data to the list
                #separated by a semi-colon
                temp = nodes_messages[node_to_send_to]
                data_to_send = temp+";"+data_to_send
                nodes_messages.update({node_to_send_to: data_to_send})

            #node_to_send_to_socket_object.send(data_to_send.encode(FORMAT))
            lock.release()
        except KeyError:
            lock.release()
            #if node not found in dictionary
            print("Node not found in registered nodes list!")
            #so that node that tried to push can take some action
            #knowing that no data was sent to the requested node
            conn.send("Node not found in registered nodes list!".encode(FORMAT))
            #connected = False

def pull_incoming_messages(conn, addr, msg, node_name):
    with lock:
        if nodes_messages[node_name]==" ":
            conn.send("[NO NEW INCOMING MESSAGES]".encode(FORMAT))
        else:    
            conn.send(nodes_messages[node_name].encode(FORMAT))

            #clear dictionary so node receives new stuff
            nodes_messages.update({node_name: " "})
    

def handle_client(conn, addr, node_name):
    
    print(f"[NEW CONNECTION] {addr}  {node_name} connected.")
    connected = True

    try:
        while connected:
            #conn.send("connection_successful".encode(FORMAT))
            
            msg = conn.recv(HEADER).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")

            #send message to client
            #conn.send("Message Received".encode(FORMAT))

            #check message command (push,pull,etc)

            #if client asks to push to another node:
            
            if msg[0:5] == "push:":
                push(conn, addr, msg, node_name)
            elif msg[0:5] == "pull:":
                pass
            elif msg == "pull_incoming_messages":
                pull_incoming_messages(conn, addr, msg, node_name)

            #conn.send("Message Received".encode(FORMAT))


        conn.close()
        print("omega")
    except ConnectionResetError:
        print(f"Connection to {node_name} lost!")

def start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        #wait for new connetion from client
        conn, addr = server.accept()

        #perform name request to "regester" the new node
        #and to determine if connection is node or message handler
        conn.send("name_request".encode(FORMAT))
        
        temp_return = conn.recv(HEADER).decode(FORMAT)

        #register the node name in the node dictionary
        if temp_return and temp_return[0:5]=="name:":
            node_name=temp_return[5:]
            #key=node_name
            #value=conn
            nodes.update({node_name: conn})
            #register the node in a dictionary of incoming messages
            nodes_messages.update({node_name: " "})

            #create a new thread to handle the new connection
            thread = threading.Thread(target=handle_client, args=(conn, addr, node_name))
            thread.start()
            
            print(f"[ACTIVE CONNETIONS] {threading.activeCount() - 1}")
        else:
            print("Node did not register, awaiting new connections.")

print("[STARTING SERVER]")
start_server()

