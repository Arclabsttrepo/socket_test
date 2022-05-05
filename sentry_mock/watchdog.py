#!/usr/bin/env python3
# client
import socket
import time
import threading
import pdb
import conversion
import select

# define constants:
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
NODE_NAME = "explore"

#declare varaibles for each quantity you want to receive
odometry = []
zed = []

#place them in a list
variableList=[None]*2 #where 2 is the amount of variables you have
#variableList=[odometry, zed]

#write their names in the same order as above
#so that these strings can be compared to the key
#to match message data with variables
variableNameList = ["odometry", "zed"]


# create client socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# attempt connection
try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print("[UNABLE TO CONNECT TO WATCHDOG]")
    print("[QUITTING]")
    quit()

# lock object needed to manage access to sockets receiving
# so far only used for receiving as no other thread is sending
# only the main thread is sending
lock = threading.Lock()
'''
#using lock with context manager:
with lock:
    #statements
# is equivalent to:
lock.aquire()
try:
    #statements
finally:
    #statements
'''


def Send_string_to_watchdog(destination,msg):
    message_string = conversion.Conversion_To_Json(destination,msg)
    message_utf = message_string.encode(FORMAT)
    msg_length = len(message_utf)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message_utf)
    print("[SENDING TO WATCHDOG] " + str(msg))


def Receive_string_from_watchdog():

    received_msg_length = client.recv(HEADER).decode(FORMAT)
    # in the event that the socket sends something blank:

    if received_msg_length:
        received_msg_length = int(received_msg_length)
        received_msg = client.recv(received_msg_length).decode(FORMAT)
        #print("[WATCHDOG SAID] " + str(received_msg))
        received_msg_dict=conversion.Json_To_Dict(received_msg)
        return received_msg_dict
    else:
        return "other connection closed"



# outgoing message handler:
def Push_to_node(node_name, msg2):
    # send command to server plus node to send message to
    Send_string_to_watchdog(node_name, msg2)


def Incoming_messages_handler(variableNameList, variableList, client):
    while True:
        received_message_dict = Receive_string_from_watchdog()

        #look for names of variabes in received message to store its latest value
        iterator = 0
        for variableNameIterator in variableNameList:
            #if variable found in the received message 
            if received_message_dict['key']==variableNameIterator:
                #store it in the corresponding variable
                with lock:
                    variableList[iterator] = received_message_dict
            iterator = iterator + 1


def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here

    while True:
        # update variables at the start of every loop

        with lock:
            #same order in decleration
            odometry=variableList[0]
            zed=variableList[1]
        print(f"odometry: {odometry}")
        print(f"zed: {zed}")
 
        time.sleep(3)

try:
    Send_string_to_watchdog("watchdog",NODE_NAME)
    thread = threading.Thread(target=Incoming_messages_handler, args=(variableNameList, variableList, client))
    thread.start()
    Main()
except KeyboardInterrupt:
    Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)

Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)
