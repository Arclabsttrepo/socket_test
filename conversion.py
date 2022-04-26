import json
import time

#destination = "client2"

#message = [[False, True],["stringy","test"]]
currenttime = time.monotonic_ns()

print(currenttime)
time.sleep(10)
currenttime = time.monotonic_ns()
print(currenttime)

def Conversion_To_Json(destination,msg):
    temp ={}
    temp.update({"key": destination})
    temp.update({"msg": msg})
    temp.update({"timestamp": currenttime})
    temp.update({"type": str(type(msg))})
    newstring = json.dumps(temp)
    #print(newstring)
    return(newstring)


#realmsg=conversiontojson(destination,message)
#PLEASE=(json.loads(json.loads(realmsg)))


def Json_To_Dict(jason):
    newdict = json.loads(jason)
    return newdict

#convert= jsontodict(realmsg)
#sendto = convert['msg']
#dest=convert['type']
#print(convert)
#print(convert['msg'][1][0])

