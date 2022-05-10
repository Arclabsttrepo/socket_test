import json
import time

def Conversion_To_Json(key,msg):
    currenttime=time.time()
    temp ={}
 
    temp.update({"key": key})
    temp.update({"msg": msg})
    temp.update({"timestamp": currenttime})
    temp.update({"type": str(type(msg))})
    newstring = json.dumps(temp)

    return(newstring)


def Json_To_Dict(jason):
    newdict = json.loads(jason)
    return newdict


#destination = "client2"

#message = [[False, True],["stringy","test"]]
#currenttime = time.monotonic_ns()

#print(currenttime)
#time.sleep(10)
#currenttime = time.monotonic_ns()
#print(currenttime)

'''def Dict_To_Json(jason):
    newstring = json.dumps(jason)
    return(newstring)'''

#realmsg=conversiontojson(destination,message)
#PLEASE=(json.loads(json.loads(realmsg)))



#convert= jsontodict(realmsg)
#sendto = convert['msg']
#dest=convert['type']
#print(convert)
#print(convert['msg'][1][0])

