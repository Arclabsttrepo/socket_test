from re import S
import client
import threading
import time

from requests import head
from math import atan2, atan, pi, cos, sin, sqrt, pow, fabs, copysign

#CONSTANTS
NODE_NAME = "controls_act"
PORT = 5050 #Port to connect to Server.
SERVER = client.socket.gethostbyname(client.socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER, PORT)

#declare varaibles for each quantity you want to receive
wheelEncoder = {}
stateMachine = {}
systemModel = {}
zedImu = {}

#place them in a list
variableList=[None]*4 #where 2 is the amount of variables you have

#write their names in the same order as above
#so that these strings can be compared to the key
#to match message data with variables
variableNameList = ["wheelEncoder", "stateMachine", "systemModel", "zedImu"]

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
    xerrBound = 0.15 #x range bound
    yerrBound = 0.1 #y range bound
    ecludVec = 0.15
    headingBound = 0.1

    #Operating variables
    xd = 0
    yd = 0
    xk = 0
    yk = 0
    wheelRps = [0,0]
    phik = 0
    timer = 0
    phidk = 0
    phidkp = 0
    exBound = 0.000001
    eyBound = 0
    flag = 0

    #Robot parameters
    ts = 2
    r = 0.11    #radius of the wheel
    d = 0.185   #distance between wheel and CoG 

    while True:
        # update variables at the start of every loop

        with client.lock:
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

        #Velocity and heading references
        vd = alpha*sqrt(pow(ex,2) + pow(ey,2))
        phidk = (atan2(ey,ex))

        if phidk < 0 and phik > 0:
            phidk = atan2(ey,ex) + 2*pi

        ephi = phidk - phik
        intekp = intek + ki*ephi # integral part
        phicdot = kp*(ephi) + intekp

        #error heading is out of phi bound
        if fabs(ephi) > ecludVec:
            vd = 0
            print("phidk: "+ str(phidk)+" phi: "+str(phik))
        else:
            print("xd: "+ str(xd) +" yd: "+ str(yd) +" xk: "+str(xk)+ " yk: "+str(yk))
        
        
        wheelLeft = (2*vd - phicdot*d)/(2*r)
        wheelRight = (2*vd + phicdot*d)/(2*r)
        wheelRps[0] = wheelLeft/(2*pi*r)
        wheelRps[1] = wheelRight/(2*pi*r)

        #We are within a bound of the desired
        if sqrt(pow(ex,2) + pow(ey,2)) < headingBound:
            wheelRps[0] = 0
            wheelRps[1] = 0
            client.Push(["state_machine"],["control"], ["NexTraj"])
            #client.Push(["client5"],["controls"],[2500.25])
            print("xd: "+ str(xd) +" yd: "+ str(yd) +" xk: "+str(xk)+ " yk: "+str(yk)+ " Lw: "+str(wheelRps[0])+ " Rw: "+str(wheelRps[1]))

        #Push(["wheel"], ["rps"], [0,0])

        phidk=phidkp

        time.sleep(0.2)




try:
    client.connectClient(ADDR)
    client.Send("watchdog","blank",NODE_NAME)
    thread = threading.Thread(target=client.Incoming_Msg_Handler, args=(variableNameList, variableList))
    thread.start()
    Main()
except KeyboardInterrupt:
    client.Send("watchdog","blank", client.DCONN_MSG)

#Send("watchdog", "blank", DCONN_MSG)