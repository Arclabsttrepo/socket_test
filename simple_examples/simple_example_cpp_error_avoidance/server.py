#!/usr/bin/env python

from http import client
from platform import node
import socket
import threading
import conversion
import pdb

# Define constants.
HEADER_SIZE = 13
PORT = 5050  #The Server port clients will connect to.
SERVER =  socket.gethostbyname(socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER,PORT)
FORMAT = 'utf-8'
DCONN_MSG = "DISCONNECT!"

# Define variables
topics = []         
nodes = {}          # A dictionary to store node names

# A locking variable to share variables between threads.
lock = threading.Lock()

#Creates the server socket with the domain as IPv4 protocol
#and the type as TCP/IP.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Binds the server to the address and port specified above.
server.bind(ADDR)

# Converts the message to a JSON string, encodes the message, gets 
# message length and creates the HEADER message and sends the HEADER
# message and actual message to the client.
def Send_To_Client(senderNode, conn, Id, msg):
    #try:
        headerDelim = "[|]"     #Stores the header delimiter that appears at the start of a message.
        escChar = "`"           #An escape character used to pad the HEADER message.        
        # Converts the message to a JSON string using a conversion library.
        jsonMsg = conversion.Conversion_To_Json(senderNode,Id,msg)
        jsonMsg += "\0"
        # Encodes the message in UTF-8 format.
        messageUTF = jsonMsg.encode(FORMAT)
        # Stores the length of the message.
        msgLength = len(messageUTF)
        # Add the delimiter and message length to the HEADER message.
        header = headerDelim + str(msgLength)
        # Pads the HEADER message to meet the length of HEADER_SIZE.
        header += escChar * (HEADER_SIZE - (len(str(msgLength))+3))
        header = header.encode(FORMAT)        
        # Sends the HEADER message to the client.
        conn.send(header)
        # Sends the actual message to the client.
        conn.send(messageUTF)
        print("[SENDING TO CLIENT] " + str(msg))
    #except:
        #print("ERROR!")

# Sends messages from one client to another using the server.
def Push(conn, msg, nodeName):
    try:
        # Lock so no other threads can access these sockets
        lock.acquire()   
        # Store the name of the node being sent to and the message.
        receiverNode = msg['key']   #Stores the node to send the msg to.
        receiverId = msg['identifier']
        msgSent = msg['msg']        #Stores the msg to be sent.
        # This checks that receiverNode exists in the dictionary. 
        # That means that the node is alive and connected. 
        # Else KeyError is raised.
        i = 0
        for x in receiverNode:
            node_to_send_to_socket_object = nodes[receiverNode[i]] #Need an array to iterate thru message
            # Sends message to client.
            Send_To_Client(nodeName, node_to_send_to_socket_object, receiverId[i], msgSent[i])
            i = i + 1
        # unlock so other threads can access these sockets
        lock.release()
    except KeyError:
        # If node not registered with watchdog, this error is thrown.
        # Unlock so other threads can access these sockets
        lock.release()
        print(str(receiverNode)+" not connected")

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


# Receives and decodes the HEADER message from each client, if a HEADER
# message is received, then receive and decode the actual mesage.
# Terminates the connection if the DISCONNECT message is received. 
def Receive_From_Client(conn,addr):
    try:
        connected = True
        # Initialize variables
        msgLength = 0         #Stores the length of the message.
        msgSession = 0        #Ensures the complete message is received.
        # Continue receiving messages from the client while the connection
        # exists.
        while connected:
            # If length of incoming message is unknown then get the HEADER
            # message to extract the length of the incoming message.
            if msgLength==0:
                # Receives and decodes the HEADER message sent by the client,
                # The no. of bytes to be received is set as HEADER_SIZE.
                header = conn.recv(HEADER_SIZE).decode(FORMAT)
                # Looks for the header delimiter "[|]" to indicate the start
                # of the HEADER message.
                headerDelim = header.find("[|]")
                # If the delimiter is found then extract the length of the
                # incoming message
                if headerDelim != -1:
                    # Message is a header
                    # Remove the header delimter ([|]) and padding (`) to 
                    # extract the length of the incoming message.
                    msgLength = header.replace("[|]", "")
                    msgLength = msgLength.replace("`", "")
                    # Store the length of the message
                    msgLength = int(msgLength)
            # If length of incoming message is known then prepare to
            # receive the message.
            if msgLength>0:
            # Receive and decode the actual message from the client
            # with the no. of bytes to be received set as the message length
            # defined in the HEADER message.
                msg = conn.recv(msgLength).decode(FORMAT)
                msg = msg.strip()
                #If the message sent by the client is the DISCONNECT message,
                #Terminate and close the connection with the server immediately.
                if msg == DCONN_MSG:
                    break
                    #Sends an acknowledgement message to the client.
                    #Serv_Send(conn,walt)
                # Display the address of the client and the message received.    
                print(f"[CLIENT: [{addr}] SAID] {msg}")
                # Converts the message received to a python dictionary.
                msgDict = conversion.Json_To_Dict(msg)
                #
                msgSession = len(msg)+msgSession
                print("MSG Session: "+ str(msgSession))
                if msgSession==msgLength:
                    msgLength=-1
                    return msgDict                  
        conn.close()
    except KeyboardInterrupt:
         print("STOP")


# Receives messages from the client after registering with the server.
def Handle_Client(conn, addr, nodeName):
    print(f"[NEW CONNECTION] {addr} {nodeName} connected.")
    connected = True
    try:
        while connected:
            msg = Receive_From_Client(conn,addr)
            # If the disconnect from watchdog message is received from client
            # Then deregister node from nodes dictionary and close connection.
            if msg['key'] == "watchdog" and msg['msg'] == DCONN_MSG:
                print(f"{nodeName} has disconnected.")
                nodes.pop(nodeName)
                connected = False
            # If the message is not for the watchdog then send to the specified client.    
            if msg['key'] != "watchdog":
                Push(conn, msg, nodeName)
        conn.close()
        print(f"[CLOSING THREAD]")
    except ConnectionResetError:
        print(f"Connection to {nodeName} lost!")
        #Deregister node from nodes list when connection is lost.
        nodes.pop(nodeName)
        conn.close()
        print(f"[CLOSING THREAD]")

#The server listens for connections, then accepts when a connection is established,
#and creates a separate thread to handle each client.
def Start():
    #The server listens for incoming connections from clients.
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        #Accepts a client's connection to the server. It blocks the execution of
        #processes until the connection is established.
        conn, addr = server.accept()
        # Stores the name of the client sending data to the watchdog.
        clientName = Receive_From_Client(conn,addr)
        # If a message is received from the client to the watchdog.
        # then attempt to register the node.
        if clientName and clientName['key'] == "watchdog":
            # Ensures only this thread can access nodes variable.
            lock.acquire()
            # Store the node name of the client.
            nodeName = clientName['msg']
            # If node already exists then close the client connection.
            if nodeName in nodes:
                print(f"{nodeName} already registered! Closing connection!")
                conn.close()
                #Allows other threads to access the nodes dictionary.
                lock.release()
            # If node does not exist then updatte nodes dictionary with
            # client name and client object.
            else:
                nodes.update({nodeName: conn})
                # Allows other threads to access the nodes dictionary.
                lock.release()
                # Creates a separate thread to process each client connection in
                # the Handle_Client function.
                thread = threading.Thread(target=Handle_Client, args=(conn, addr, nodeName))
                thread.start()
                #Keeps track of the number of clients connected to the server.
                #NB. A thread is subtracted from the count to exclude the server thread.
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")
        else:
            print("[NODE DID NOT REGISTER] Awaiting new connections.")

#Main code execution.
try:
    print("[STARTING] Watchdog is starting...")
    Start()

except KeyboardInterrupt:
    print("Stop!")
