import json
import time

def Conversion_To_Json(key,identifier,msg):
    currenttime=time.time()
    temp ={}
   # keys =[key]
   # msgs= [msg]
    msgtype = type(msg)
    if (str(type(msg))=="<class 'list'>"):
        msgtype = type(msg[0])
    temp.update({"key": key})
    temp.update({"identifier": identifier})
    temp.update({"msg": msg})
    temp.update({"timestamp": currenttime})
    temp.update({"type": str(msgtype)})
    newstring = json.dumps(temp)

    return(newstring)


def Json_To_Dict(jason):
    newdict = json.loads(jason)
    return newdict


#destination = ["client2","client1"]
#identifier = ["sample1","sample2"]
#message = [150964565.352, "Hello"]
#newstring = Conversion_To_Json(destination, identifier, message)

#newdict = Json_To_Dict(newstring)
#print(newstring)


#print (newdict["msg"])
#print(newstring)
#currenttime = time.monotonic_ns()

#print(currenttime)
#time.sleep(10)
#currenttime = time.monotonic_ns()
#print(currenttime)

'''def Dict_To_Json(jason):
    newstring = json.dumps(jason)
    return(newstring)'''

#realmsg=Conversion_To_Json(destination,message)
#print(realmsg)
#PLEASE=(json.loads(json.loads(realmsg)))



#convert= jsontodict(realmsg)
#sendto = convert['msg']
#dest=convert['type']
#print(convert)
#print(convert['msg'][1][0])

#-----testing arrays----

