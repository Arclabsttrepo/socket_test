#!/usr/bin/env python3
# client
from curses import init_pair
import socket
import time
import threading
import pdb
import conversion
import pyzed.sl as sl
import math


# define constants:
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
NODE_NAME = "zed"



# create client socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# attempt connection
'''
try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print("[UNABLE TO CONNECT TO WATCHDOG]")
    print("[QUITTING]")
    quit()'''

# lock object needed to manage access to sockets receiving
# so far only used for receiving as no other thread is sending
# only the main thread is sending
#lock = threading.Lock()
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
        print("[WATCHDOG SAID] " + str(received_msg))
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





def Main():
    # run main code here
    # process robotic algorthm here
    # compute stuff here

    image = sl.Mat()
    depth_map = sl.Mat()
    point_cloud = sl.Mat()

    
    runtime_parameters = sl.RuntimeParameters()
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        # A new image and depth is available if grab() returns SUCCESS
        zed.retrieve_image(image, sl.VIEW.LEFT) # Retrieve the left image
        zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH) # Retrieve depth
        
        width=depth_map.get_width()
        print(f"width: {width}")
        height=depth_map.get_height()
        print(f"height: {height}")
        #x = round(image.get_width() / 2)
        #y = round(image.get_height() / 2)
        count = 0
        
        for x in range(width):
            for y in range(height): 
                depth_value = depth_map.get_value(x,y)
                print(depth_value)
                print
                count = count +1
                
        #print(f"count: {count}")







'''        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
        x = round(image.get_width() / 2)
        y = round(image.get_height() / 2)  
        err, point_cloud_value = point_cloud.get_value(x, y)  

        distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] + point_cloud_value[1] * point_cloud_value[1] + point_cloud_value[2] * point_cloud_value[2])
        print(distance)'''
    #while True:
        # update variables at the start of every loop
        # topic variables and node messages
        # use Receive_string_from_watchdog()






        #Push_to_node("explore", [z,y])
        #time.sleep(1)



zed = sl.Camera()

#Set configuration parameters
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD2K
#init_params.camera_fps=15
init_params.depth_mode = sl.DEPTH_MODE.ULTRA # Use ULTRA depth mode


#print(zed.get_camera_informations().camera_resolution)

#Open the camera
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    exit(-1)

resolution = zed.get_camera_information().camera_resolution
print(resolution.height)
try:
    #Send_string_to_watchdog("watchdog",NODE_NAME)
    Main()
except KeyboardInterrupt:
    #Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)
    zed.close()

#Send_string_to_watchdog("watchdog", DISCONNECT_MESSAGE)
