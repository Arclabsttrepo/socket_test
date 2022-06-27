import json
import time

def Conversion_To_Json(key,identifier,msg):
    currenttime=time.time()
    temp = {}
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