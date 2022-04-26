import json

#def conversion(jason)
    
destination = "client2"

sample= '''
{
    "velocity":
    {
    "type":"int32",
    "data":25
    }
    
}
'''

sample2 = '''

    
    {
    "type":"int32",
    "data":0
    }


'''


testing = json.dumps(sample2)
testing2 = json.loads(json.loads(testing))

print(testing2)
print(testing)
#for value in test2['velocity']:
 #   print(value['type'])





x = 5.56

#convert(test2)


testing2['data'] = x + 7.53

#print(type(test2['data']))
#print(test2['data'])
teststring = json.dumps(testing2)




#def jsontostring(test2):
