#include "cppclient.h"

#define NODE_NAME "client5"
#define PORT 5050
#define SERVER "127.0.1.1"

int main(){
    json variableList = json::array();
    variableList = {};
    json variableNameList = json::array();
    variableNameList = {"controls", "model"};

    json controls;
    json model;

    int sock = connect(PORT, SERVER);
    Send(sock, "watchdog", "blank", NODE_NAME);

    while(true){
        for(x = 0; x < )
        

        json testobj = Receive(sock);
        std::cout << testobj["identifier"] <<std::endl;
    }   

  

return 0;
}