# client
import socket
import time
import threading

# define constants:
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
NODE_NAME = "client2"

received_from_node = ""

# create client socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# attempt connection
try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print("[UNABLE TO CONNECT TO WATCHDOG]")
    print("[QUITTING]")
    quit()

# lock object needed to manage access to sockets receving
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


def Send_string_to_watchdog(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print("[SENDING TO WATCHDOG] " + msg)


def Receive_string_from_watchdog():
    loopUntilMessageReceived = True
    received_msg_length = client.recv(HEADER).decode(FORMAT)
    # in the event that the socket sends something blank:
    while loopUntilMessageReceived:
        if received_msg_length:
            received_msg_length = int(received_msg_length)
            received_msg = client.recv(received_msg_length).decode(FORMAT)
            print("[WATCHDOG SAID] " + received_msg)
            loopUntilMessageReceived = False
            return received_msg







def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here
    x = 0
    while True:
        # update variables at the start of every loop
        # topic varaibles and node messages
        # use receive_string_from_watchdog()
        print(Receive_string_from_watchdog())

        time.sleep(15)


Send_string_to_watchdog("name:" + NODE_NAME)

try:
    Main()
except KeyboardInterrupt:
    Send_string_to_watchdog(DISCONNECT_MESSAGE)

Send_string_to_watchdog(DISCONNECT_MESSAGE)
