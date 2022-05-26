import server

PORT = 5050  #The Server port clients will connect to.
SERVER =  server.socket.gethostbyname(server.socket.gethostname()) #"127.0.0.1"
ADDR = (SERVER,PORT)

#Main code execution.
try:
    server.connectServer(ADDR)
    print("[STARTING] Watchdog is starting...")
    server.Start()

except KeyboardInterrupt:
    print("Stop!")