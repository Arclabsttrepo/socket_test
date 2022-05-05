#!/usr/bin/env python3
# client
import socket
import time
import threading
import pdb
import conversion
import pyzed.sl as sl

# define constants:
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
NODE_NAME = "zed"



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
#lock = threading.Lock()
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
        print("[WATCHDOG SAID] " + str(received_msg))
        received_msg_dict=conversion.Json_To_Dict(received_msg)
        return received_msg_dict
    else:
        return "other connection closed"



# outgoing message handler:
def Push_to_node(node_name, msg2):
    # send command to server plus node to send message to

    Send_string_to_watchdog(node_name, msg2)
    '''
    try:
        # pdb.set_trace()
        #Send_string_to_watchdog("push:"+msg2)
        Send_string_to_watchdog("push", node_name, msg2)
        #temp = Receive_string_from_watchdog()
        #if temp == "node_found_push_the_data":

        #    Send_string_to_watchdog(msg2)
            # print(Receive_string_from_watchdog())
        #else:
        #    print(f"[{NODE_NAME}] says: Pushing to {node_name} failed!")
    except AttributeError:
        print("Incorrect data type sent, recheck")
        quit()
    '''





def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here
    z = 0.1
    y = 0.2
    x = 0
    
    while True:
        # update variables at the start of every loop
        # topic variables and node messages
        # use Receive_string_from_watchdog()

        #Push_to_node("client2", str(x))
        z = z + 0.2
        y = y + 0.1
        #Push_to_node("client2", str(x))

        Push_to_node("explore", [z,y])
        time.sleep(1)
        x = x + 1
        print(x)
        #Receive_string_from_watchdog()





try:
    Send_string_to_watchdog("watchdog",NODE_NAME)
    Main()
except KeyboardInterrupt:
    Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)

Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)
