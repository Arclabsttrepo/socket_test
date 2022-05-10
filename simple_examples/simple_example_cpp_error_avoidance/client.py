from re import S
import socket
import threading
import time
import conversion


#CONSTANTS
HEADER_SIZE = 13
PORT = 5050 #Port to connect to Server.
SERVER = socket.gethostbyname(socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DCONN_MSG = "DISCONNECT!" #Message used to disconnect the client from the server.
NODE_NAME = "client1"

#Creates the client socket with the domain as IPv4 protocol
#and the type as TCP/IP.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    #Establishes a connection to the server at the address and port specified above.
    client.connect(ADDR)
except ConnectionRefusedError:
    print("[UNABLE TO CONNECT TO WATCHDOG]")
    print("[QUITTING]")
    quit() 

# Lock object needed o manage access to sockets
lock = threading.Lock()


#Encodes messages, gets the message length, creates the header message,
#which contains the length of the actual message, and sends the header
#message and actual message to the server, in that order. Then attempts
#to receive a response from the server.
# A header message is of the form below
# (headerdelimiter)(messagelength)(padding)
# eg. [|]3`````````
def Send(destNode, msg):
    try:
        headerDelim = "[|]"     #Stores the header delimiter that appears at the start of a message.
        escChar = "`"           #An escape character used to pad the HEADER message.
        jsonMsg = conversion.Conversion_To_Json(destNode, msg)
        # Encodes the message in UTF-8 format.
        message = jsonMsg.encode(FORMAT)
        # Stores the length of the message.
        msgLength = len(message)
        # Add the delimiter and message length to the HEADER message.
        header = headerDelim + str(msgLength)
        # Pads the HEADER message to meet the length of HEADER_SIZE.
        header += escChar * (HEADER_SIZE - (len(str(msgLength))+3))
        header = header.encode(FORMAT)
        #Sends the HEADER message to the server.
        client.send(header)
        #Sends the actual message to the server.
        client.send(message)
        #Receive()
    except:
        print("ERROR!")

#Receives and decodes the HEADER  message from the client, if a HEADER
#message is received, then receive and decode the actual message.
def Receive():
    try:
        #Receives and decodes the HEADER message sent by the server.
        #The no. of bytes to be received is set as HEADER_SIZE.
        servMsglength = client.recv(HEADER_SIZE).decode(FORMAT)
        #If the HEADER message is received, then convert the HEADER message
        #to an integer, receive and decode the actual message from the server
        #with the no. of bytes to be received set as the integer defined 
        #in the HEADER message.
        if servMsglength:
            servMsglength = int(servMsglength)
            servMsg = client.recv(servMsglength).decode(FORMAT)
            print(servMsg)
            print(len(servMsg))
    except:
        print("ERRRRROR!")

def Push(nodeName, msg):
    Send(nodeName, msg)

def Main():
    while True:
        #dict = {"datatype": "int32", "dta": [40,32,24,16,8,0,1,2,3,4,5,6,7,8,9,10,11,12], "identifier": "A1"}
        dict = 22
        Push("client2", dict)
        time.sleep(1)
        Receive()
        break


Send("watchdog", NODE_NAME)

try:
    Main()
except KeyboardInterrupt:
    Send("watchdog", DCONN_MSG)
#walt = "Hello"
#jason = json.dumps(dict)
#time.sleep(5)
#Send(jason)
Send("watchdog",DCONN_MSG)
