#!/usr/bin/env python

import socket
import threading
import pdb

HEADER_SIZE = 64
PORT = 1905  #The Server port clients will connect to.
SERVER = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)
FORMAT = 'utf-8'
DCONN_MSG = "DISCONNECT!"


walt = "Hello from the super amazing fantastic special Server"
john = walt.encode(FORMAT)


#Creates the server socket with the domain as IPv4 protocol
#and the type as TCP/IP.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Binds the server to the address and port specified above.
server.bind(ADDR)

#Receives and decodesthe HEADER message from each client, if a HEADER,
#message is received, then receive and decode the actual mesage.
#Terminates the connection if the DISCONNECT message is received. 
def Handle_Client(conn,addr):
    try:
        print(f"[NEW CONNECTION] {addr} connected.")
        connected = True
        #Continue receiving messages from the client while the connection
        #exists.
        while connected:
            #Receives and decodes the HEADER message sent by the client,
            #The no. of bytes to be received is set as HEADER_SIZE.
            msgLength = conn.recv(HEADER_SIZE).decode(FORMAT)
            #If the HEADER message is received, then convert the HEADER message
            #to an integer, receive and decode the actual message from the client
            #with the no. of bytes to be received set as the integer defined 
            #in the HEADER message.
            if msgLength:
                msgLength = int(msgLength)
                msg = conn.recv(msgLength).decode(FORMAT)
                #If the message sent by the client is the DISCONNECT message,
                #Terminate and close the connection with the server immediately.
                if msg == DCONN_MSG:
                    break
                #Sends an acknowledgement message to the client.
                Serv_Send(conn,walt)
                print(f"[{addr}] {msg}")
        conn.close()
    except KeyboardInterrupt:
         print("STOP")

#Encodes messages, gets the message length, creates the header message,
#which contains the length of the actual message, and sends the header
#message and actual message to the client, in that order.
def Serv_Send(conn, servMsg):
    try:
        #Adds a NULL terminator at the end of the message, specifically for
        #C++ correct intepretation of message.
        servMsg += "\0"
        #Encodes the message to be set in UTF-8 format.
        message = servMsg.encode(FORMAT)
        #Creates the HEADER message to be sent by encoding the message
        #length as a string in UTF-8 format and packing the HEADER with
        #blank spaces (in UTF-8 notation) to fill the HEADER message with
        #the no. of bytes the client expects to receive (i.e HEADER_SIZE).        
        servMsglength = len(message)
        servSendlength = str(servMsglength).encode(FORMAT)
        servSendlength += b' ' * (HEADER_SIZE - len(servSendlength))
        #Sends the HEADER message to the client.
        conn.send(servSendlength)
        #Sends the actual message to the client.
        conn.send(message)
    except:
        print("ERROR!")

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
        #Creates a separate thread to process each client connection in
        #the Handle_Client function.
        thread = threading.Thread(target=Handle_Client, args=(conn, addr))
        thread.start()
        #Keeps track of the number of clients connected to the server.
        #MB. A thread is subtracted from the count to exclude the server thread.
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")


try:
    print("[STARTING] Watchdog is starting...")
    Start()

except KeyboardInterrupt:
    print("Stop!")
