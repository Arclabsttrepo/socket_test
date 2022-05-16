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
def Send(destNode, id, msg):
    try:
        headerDelim = "[|]"     #Stores the header delimiter that appears at the start of a message.
        escChar = "`"           #An escape character used to pad the HEADER message.
        # Converts the message to a JSON string using a conversion library.
        jsonMsg = conversion.Conversion_To_Json(destNode, id, msg)
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

# Receives and decodes the HEADER  message from the client, if a HEADER
# message is received, then receive and decode the actual message.
def Receive():
    try:
        msgLength = 0         #Stores the length of the message.
        msgSession = 0        #Ensures the complete message is received.
        # If length of incoming message is unknown then get the HEADER
        # message to extract the length of the incoming message.
        if msgLength==0:
            # Receives and decodes the HEADER message sent by the client,
            # The no. of bytes to be received is set as HEADER_SIZE.
            header = client.recv(HEADER_SIZE).decode(FORMAT)
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
        if msgLength>0:
        # Receive and decode the actual message from the client
        # with the no. of bytes to be received set as the message length
        # defined in the HEADER message.
            msg = client.recv(msgLength).decode(FORMAT)
            print(time.time())
            msg = msg.strip()
            # Converts the message received to a python dictionary.
            msgDict = conversion.Json_To_Dict(msg)
            print("[WATCHDOG SAID] " + str(msg))
            msgLength = -1
            return msgDict
    except:
        print("ERRRRROR!")

def Push(nodeName, id, msg):
    Send(nodeName, id, msg)

def Main():
    while True:
        #dict = {"datatype": "int32", "dta": [40,32,24,16,8,0,1,2,3,4,5,6,7,8,9,10,11,12], "identifier": "A1"}
        dict = ["nonsense"]
        Push(["client2"], ["topic"], dict)
        time.sleep(1)
        Receive()
        break


Send(["watchdog"], ["blank"], NODE_NAME)

try:
    Main()
except KeyboardInterrupt:
    Send(["watchdog"],["blank"],DCONN_MSG)

Send(["watchdog"],["blank"],DCONN_MSG)