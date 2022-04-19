#client
import socket
import time
import threading

#define constants:
HEADER = 2048
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
NODE_NAME = "client3"

received_from_node=""

#create client socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#attempt connection
try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print("[UNABLE TO CONNECT TO WATCHDOG]")
    print("[QUITTING]")
    quit()

#lock object needed to manage access to sockets receving
#so far only used for receiving as no other thread is sending
#only the main thread is sending
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

def send_string_to_watchdog(msg):
    message = msg.encode(FORMAT)
    client.send(message) 
    print("[SENDING TO WATCHDOG] " + msg)

def receive_string_from_watchdog():
    received_msg=client.recv(2048).decode(FORMAT)
    print("[WATCHDOG SAID] " + received_msg)
    return received_msg

def register_node_with_watchdog():
    if client.recv(2048).decode(FORMAT) == "name_request":
    #register with server:
        send_string_to_watchdog("name:"+NODE_NAME)

#outgoing message handler:    
def push_to_node(node_name, msg):
    #send command to server plus node to send message to
    #node name and msg sperate for now
    #as node may have variable name length
    send_string_to_watchdog("push:"+node_name)
    temp = receive_string_from_watchdog()
    if temp == "node_found_push_the_data":
        send_string_to_watchdog(msg)
        #print(receive_string_from_watchdog())
    else:
        print(f"[{NODE_NAME}] says: Pushing to {node_name} failed!")

def pull_incoming_messages():
    send_string_to_watchdog("pull_incoming_messages")
    receive_string_from_watchdog()

        

def main():
    #run main code here
    #process robotic algorthm here
    #compute stuff here
    x=0
    while True:
        #update variables at the start of every loop
        #topic varaibles and node messages
        #use receive_string_from_watchdog()

        push_to_node("client1", "Hello From client3")
        time.sleep(5)



register_node_with_watchdog()


main()

send_string_to_watchdog(DISCONNECT_MESSAGE)