#include <iostream>
#include <ctime>
#include "nlohmann/json.hpp"
#include <typeinfo>

using json= nlohmann::json;

std::string Convert_to_json(json key, json identifier, json msg)
{

std::time_t result = std::time(nullptr);
json convert = {
    {"key", key},
    {"identifier", identifier},
    {"msg", msg},
    {"type", "in progress"},
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