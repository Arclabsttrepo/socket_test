#include <iostream>
#include <ctime>
#include "nlohmann/json.hpp"
#include <typeinfo>


using json= nlohmann::json;

//Converts messages received to a standard JSON format
std::string Convert_to_json(json key, json identifier, json msg)
{

std::string msgType = "";

switch(msg.type()){
    case json::value_t::number_integer:
        msgType = "int";
        break;
    case json::value_t::number_float:
        msgType = "float";
        break;
    case json::value_t::string:
        msgType = "string";
        break;
    case json::value_t::array:
        if(msg[0].type() == json::value_t::number_integer){
            msgType = "int array";
        } else if (msg[0].type() == json::value_t::number_float){
            msgType = "float array";
        } else if (msg[0].type() == json::value_t::string){
            msgType = "string array";
        } else if (msg[0].type() == json::value_t::boolean){
            msgType = "bool array";
        } else {
            msgType = "unclear";
        }
        break;
    case json::value_t::boolean:
        msgType = "bool";
        break;
    default:
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