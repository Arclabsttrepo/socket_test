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

odometry = []
zed = []

odometryTemp = []
zedTemp = []

variableList=[odometry, zed]
#put in the same order as above
variableNameListTemp = ["odometry", "zed"]

#put in the same order as above
variableListTemp=[odometryTemp, zedTemp]

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

def Incoming_messages_handler(variableNameListTemp, variableListTemp, client):
    while True:
        
        received_message_dict = Receive_string_from_watchdog()
        
        #look for names of variabes in received msg to store its value
        for variableIndex in range(len(variableNameListTemp)):
            #if variable found in the received message
            
            if received_message_dict['key']==variableNameListTemp[variableIndex]:
                #store it in the corresponding variable
                with lock:
                    variableListTemp[variableIndex]=received_message_dict['msg']
                    #print(received_message_dict['msg'])
                #print(str(variableList[variable_index]))




        '''
        #is there new data in the receive buffer?
        socket_buffer_readable, _, _ = select.select([client],[],[],0) #what to do with algortihm that needs data if this doesn't get any?????
        print(socket_buffer_readable)
        #if yes:
        while socket_buffer_readable:
            
            received_message_dict = Receive_string_from_watchdog()
            #look for names of variabes in received msg to store its value
            for variableIndex in range(len(variableNameListTemp)):
                #if variable found in the received message
                
                if received_message_dict['key']==variableNameListTemp[variableIndex]:
                    #store it in the corresponding variable
                    with lock:
                        variableListTemp[variableIndex]=received_message_dict['msg']
                    #print(str(variableList[variable_index]))

            
            if temp['key']=="odometry":
                print(temp['msg'])
            elif temp['key']=="zed":
                print(temp['msg'])                   
             
            

            #check again so you can loop until you get ALL the items in the buffer
            socket_buffer_readable, _, _ = select.select([client],[],[],0)    
        '''


def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here
    x = 0
    y = 0
    #Push_to_node("client2", "Hello yeah")
    while True:
        # update variables at the start of every loop
        # topic variables and node messages
        # use Receive_string_from_watchdog()

        #update variables here

        with lock:
            for variableIndex in range(len(variableList)):
                variableList[variableIndex] = variableListTemp[variableIndex]
    
        for variableIndex in range(len(variableList)):
            print(variableList[variableIndex])
            print("test")

        '''
        #is there new data in the receive buffer?
        socket_buffer_readable, _, _ = select.select([client],[],[],0) #what to do with algortihm that needs data if this doesn't get any?????
        
        #if yes:
        while socket_buffer_readable:
            Receive_string_from_watchdog()
            #check again so you can loop until you get ALL the items in the buffer
            socket_buffer_readable, _, _ = select.select([client],[],[],0)    
        '''


        #run algorithm here:
        time.sleep(3)






try:
    Send_string_to_watchdog("watchdog",NODE_NAME)
    thread = threading.Thread(target=Incoming_messages_handler, args=(variableNameListTemp, variableListTemp, client))
    thread.start()
    Main()
except KeyboardInterrupt:
    Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)

Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)
