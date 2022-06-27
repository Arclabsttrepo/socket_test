#include <iostream>
#include <ctime>
#include "nlohmann/json.hpp"
#include <typeinfo>


using json= nlohmann::json;

//Converts messages received to a standard JSON format
std::string Convert_to_json(json key, json identifier, json msg)
{

std::string msgType = "";

//Checks the data type of the JSON object "msg"
if(msg.type() == json::value_t::number_integer){
    msgType = "int";
} else if (msg.type() == json::value_t::number_float){
    msgType = "float";
} else if (msg.type() == json::value_t::string){
    msgType = "string";
} else if (msg.type() == json::value_t::array){
    msgType = "array";
} else if (msg.type() == json::value_t::boolean){
    msgType = "bool";
} else {
    msgType = "unclear";
}

std::time_t result = std::time(nullptr);

json convert = {
    {"key", key},
    {"identifier", identifier},
    {"msg", msg},
    {"type", msgType},
    {"timestamp", result}
    
};
std::string dumpstr = convert.dump();
return dumpstr;
}

json Json_to_object(std::string jason)
{
json newobject = json::parse(jason);;
return newobject;

}