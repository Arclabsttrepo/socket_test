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
        json testobj = Receive(sock);
        for(int x = 0; x < variableNameList.size(); x++){
            if(testobj["identifier"]==variableNameList[x]){
                variableList[x] = testobj; 
            }
        }

        controls = variableList[0];
        model = variableList[1];        

        std::cout << controls <<std::endl;
        std::cout << model <<std::endl;

    }   

  

return 0;
}