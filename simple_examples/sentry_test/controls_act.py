from re import S
import socket
import threading
import time

from requests import head
import conversion
from math import atan2, atan, pi, cos, sin, sqrt, pow, fabs, copysign


#CONSTANTS
HEADER_SIZE = 13
PORT = 5050 #Port to connect to Server.
SERVER = socket.gethostbyname(socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DCONN_MSG = "DISCONNECT!" #Message used to disconnect the client from the server.
NODE_NAME = "controls_act"


#declare varaibles for each quantity you want to receive
wheelEncoder = {}
stateMachine = {}
systemModel = {}
zedImu = {}

#place them in a list
variableList=[None]*4 #where 2 is the amount of variables you have
#variableList=[odometry, zed]

#write their names in the same order as above
#so that these strings can be compared to the key
#to match message data with variables
variableNameList = ["wheelEncoder", "stateMachine", "systemModel", "zedImu"]

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
            #print(time.time())
            msg = msg.strip()
            #Removes null terminator implemented to handle c++ clients.
            msg = msg.replace("\0", "")
            # Converts the message received to a python dictionary.
            msgDict = conversion.Json_To_Dict(msg)
            #print("[WATCHDOG SAID] " + str(msg))
            msgLength = -1
            return msgDict
    except:
        print("ERRRRROR!")

def Push(nodeName, id, msg):
    Send(nodeName, id, msg)

def Incoming_Msg_Handler(variableNameList, variableList):
    while True:
        receivedMsg = Receive()
        #look for names of variables in received message to store its latest value
        index = 0
        for variableNameIterator in variableNameList:
            #if variable found in received message
            if receivedMsg['identifier']==variableNameIterator:
                with lock:
                    variableList[index] = receivedMsg
            index = index + 1



def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here
    
    print("CONTROLS HAS STARTED")

    alpha = 0.1
    kp = 0.1
    ki = 0.001
    intek = 0

    #Bounds
    xerrBound = 0.2 #x range bound
    yerrBound = 0.1 #y range bound
    ecludVec = 0.5
    headingBound = 0.2

    #Operating variables
    xd = 0
    yd = 0
    xk = 0
    yk = 0
    wheelRps =[0,0]
    phik = 0
    timer = 0
    phidk = 0
    exBound = 0.000001
    eyBound = 0
    flag = 0

    #Robot parameters
    ts = 2
    r = 0.11
    d = 0.185  

    while True:
        # update variables at the start of every loop

        with lock:
            #same order in decleration
            wheelEncoder = variableList[0]
            stateMachine = variableList[1]
            systemModel = variableList[2]
            zedImu = variableList[3]
        print(f"wheelEncoder: {wheelEncoder}")
        print(f"state: {stateMachine}")
        print(f"systemModel: {systemModel}")
        print(f"zedImu: {zedImu}")

        if stateMachine is None:
            xd = 0
            yd = 0
        else:
            xd = stateMachine["msg"][0]
            yd = stateMachine["msg"][1]
            flag = stateMachine["msg"][3]
        if systemModel is None:
            xk = 0
            yk = 0
            phik = 0
        else:
            xk = systemModel["msg"][0]
            yk = systemModel["msg"][1]
            phik = systemModel["msg"][2]
        
        #Develop errors for controls
        ex = xd - xk
        ey = yd - yk

        #error bounds to be within goal
        if fabs(ex) <= xerrBound:
            ex = exBound
        if fabs(ey) <= yerrBound:
            ey = eyBound

        vd = alpha*sqrt(pow(ex,2) + pow(ey,2))
        phidk = (atan2(ey,ex))

        ephi = phidk - phik
        intekp = intek + ki*ephi # integral part
        phicdot = kp*(ephi) + intekp

        #bounded condition for turning
        if fabs(ephi) > ecludVec:
            vd  = 0
        
        wheelLeft = (2*vd - phicdot*d)/(2*r)
        wheelRight = (2*vd + phicdot*d)/(2*r)
        wheelRps[0] = wheelLeft/(2*pi*r)
        wheelRps[1] = wheelRight/(2*pi*r)

        #We are within a bound of the desired
        if sqrt(pow(ex,2) + pow(ey,2)) < headingBound:
            wheelRps[0] = 0
            wheelRps[1] = 0
            #Push(["state_machine"],["control"], ["NexTraj"])
            Push(["client5"],["controls"],[2500.25])
            print("xd: "+ str(xd) +" yd: "+ str(yd) +" xk: "+str(xk)+ " yk: "+str(yk)+ " Lw: "+str(wheelRps[0])+ " Rw: "+str(wheelRps[1]))

        #Push(["wheel"], ["rps"], [0,0])

        time.sleep(3)




try:
    Send("watchdog","blank",NODE_NAME)
    thread = threading.Thread(target=Incoming_Msg_Handler, args=(variableNameList, variableList))
    thread.start()
    Main()
except KeyboardInterrupt:
    Send("watchdog","blank", DCONN_MSG)

Send("watchdog", "blank", DCONN_MSG)