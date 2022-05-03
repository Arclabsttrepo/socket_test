from re import S
import socket
import time
import json


#CONSTANTS
HEADER_SIZE = 64
PORT = 1905 #Port to connect to Server.
SERVER = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DCONN_MSG = "DISCONNECT!" #Message used to disconnect the client from the server.

#Creates the client socket with the domain as IPv4 protocol
#and the type as TCP/IP.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Establishes a connection to the server at the address and port specified above.
client.connect(ADDR)

#Encodes messages, gets the message length, creates the header message,
#which contains the length of the actual message, and sends the header
#message and actual message to the server, in that order. Then attempts
#to receive a response from the server.
def Send(msg):
    try:
        #Encodes the messsage to be set in UTF-8 format.
        message = msg.encode(FORMAT)
        #Stores the message length.
        msgLength = len(message)
        #Creates the HEADER message to be sent by encoding the message
        #length as a string in UTF-8 format and packing the HEADER with
        #blank spaces (in UTF-8 notation) to fill the HEADER message with
        #the no. of bytes the server expects to receive (i.e HEADER_SIZE).
        sendLength = str(msgLength).encode(FORMAT)
        sendLength += b' ' * (HEADER_SIZE - len(sendLength))
        #Sends the HEADER message to the server.
        client.send(sendLength)
        #Sends the actual message to the server.
        client.send(message)
        Receive()
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
        print("ERROR!")


dict = {"datatype": "int32", "data": [40,32,24,16,8,0,1,2,3,4,5,6,7,8,9,10,11,12], "identifier": "A1"}
walt = "Hello"
jason = json.dumps(dict)
time.sleep(5)
Send(jason)
Send(DCONN_MSG)
