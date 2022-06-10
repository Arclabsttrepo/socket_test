from re import S
import client
import threading
import time

#CONSTANTS
NODE_NAME = "state_machine"
PORT = 5050 #Port to connect to Server.
SERVER = client.socket.gethostbyname(client.socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER, PORT)

#declare varaibles for each quantity you want to receive
navSensor = {}
stateVector = {}
controlAct = {}

#place them in a list
variableList=[None]*3 #where 2 is the amount of variables you have
#variableList=[odometry, zed]

#write their names in the same order as above
#so that these strings can be compared to the key
#to match message data with variables
variableNameList = ["nav", "state", "control"]

def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here
    global ready
    print("STATE MACHINE HAS STARTED")
    ready = True

    xdestraj=[0,1.5,1.5,0,0]
    ydestraj=[0,0,1.5,1.5,0]   

    xd = 0
    yd = 0
    phid = 0
    flag = -1
    localNavEngaged = 0 
    iter = 0 

    while True:
        # update variables at the start of every loop

        with client.lock:
            #same order in decleration
            navSensor = variableList[0]
            stateVector = variableList[1]
            controlAct = variableList[2]
        print(f"nav: {navSensor}")
        print(f"state: {stateVector}")
        print(f"control: {controlAct}")
        if stateVector is None:
            xk = 0
            yk = 0
            phik = 0
        else:    
            xk=stateVector["msg"][0]
            yk=stateVector["msg"][1]
            phik=stateVector["msg"][2]

        #Push(["nav"],["state"],[[xk,yk,phik]])

        # #Determine if we need to stop before traversing

        # cxd=nav_sensor_callback_data[0]
        # cyd=nav_sensor_callback_data[1]
        # cphid=nav_sensor_callback_data[2]
        # print("Zxd: "+ str(cxd)+ " Zyd: "+ str(cyd), " Zphid: "+ str(cphid))

        xd = xdestraj[iter]
        yd = ydestraj[iter]

        if controlAct is None:
            controlActData = "null"
        else:
            controlActData = controlAct["msg"]
        if controlActData == "NexTraj":
            controlActData = ""
            if iter < len(xdestraj) - 1:
                print("Next Goal")
                iter = iter+1
                xd = xdestraj[iter]
                yd = ydestraj[iter]
            flag = 0
        
        client.Push(["controls_act"],["stateMachine"], [[xd,yd,phid,flag]])
        print("xd: "+ str(xd)+ " yd: "+ str(yd)+ " phid: "+ str(phid) +" iter: "+ str(iter))

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