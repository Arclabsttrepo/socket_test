from re import S
import client
import threading
import time
from math import atan2, atan, pi, cos, sin, sqrt, pow, fabs, copysign

#CONSTANTS
NODE_NAME = "system_model"
PORT = 5050 #Port to connect to Server.
SERVER = client.socket.gethostbyname(client.socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER, PORT)

#declare varaibles for each quantity you want to receive
wheelEncoder = {}
zedImu = {}

#place them in a list
variableList=[None]*2 #where 2 is the amount of variables you have

#write their names in the same order as above
#so that these strings can be compared to the key
#to match message data with variables
variableNameList = ["wheelEncoder", "zedImu"]

def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here
    print("SYSTEM MODEL HAS STARTED")

    #Robot Parameters
    ts = 2
    r = 0.1143
    d = 0.185

    #Set Operating variables

    xk = 0
    yk = 0
    phik = 0
    timer = 0
    state_vector = [0,0,0]
    initial_state_vector = [0,0,0]

    while True:
        # update variables at the start of every loop
        with client.lock:
            #same order in decleration
            wheelEncoder = variableList[0]
            zedImu = variableList[1]
        print(f"wheel encoder: {wheelEncoder}")
        print(f"zed: {zedImu}")

        if wheelEncoder is None:
            encoderVelLeft = 0
            encoderVelRight = 0
        else:
            encoderVelLeft = wheelEncoder["msg"][0]
            encoderVelRight = wheelEncoder["msg"][1]
        
        wheelRightVel = 2*pi*r*encoderVelRight
        wheelLeftVel = 2*pi*r*encoderVelLeft

        if timer == 0:
            xk = initial_state_vector[0]
            yk = initial_state_vector[1]
            phik = initial_state_vector[2]
        
        #State space system and Euler Backward Integral Solver
        xkp = xk + ts*(r/2)*(wheelRightVel+wheelLeftVel)*cos(phik)
        ykp = yk + ts*(r/2)*(wheelRightVel+wheelLeftVel)*sin(phik)
        phikp = phik + ts*(r/(2*d))*(wheelRightVel-wheelLeftVel)
        timer = timer + 1        

        #Reset heading angle for full rotation in both directions
        if fabs(phikp) > pi*2:
            phikp = phikp - 2*pi

        print("xk: "+ str(xkp)+ " yk: "+str(ykp)+ " phik: "+str(phikp))

        #Set next values
        xk = xkp
        yk = ykp
        phik = phikp

        state_vector = [xk,yk,phik]
        client.Push(["state_machine", "controls_act"],["state", "systemModel"], [state_vector, state_vector])

        time.sleep(0.2)

        #Testing C++ client5
        #client.Push(["client5"],["model"],[1523.25])
        #time.sleep(3)

try:
    client.connectClient(ADDR)
    client.Send("watchdog","blank",NODE_NAME)
    thread = threading.Thread(target=client.Incoming_Msg_Handler, args=(variableNameList, variableList))
    thread.start()
    Main()
except KeyboardInterrupt:
    client.Send("watchdog","blank", client.DCONN_MSG)

#Send("watchdog", "blank", DCONN_MSG)