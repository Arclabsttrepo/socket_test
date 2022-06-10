#include "client.hpp"

#define NODE_NAME "client5"
#define PORT 5050
#define SERVER "127.0.1.1"

int main(){
  json variableList = json::array();
  variableList = {};
  json variableNameList = json::array();
  variableNameList = {"state"};

  json state;

  int sock = connectClient(PORT, SERVER);
  Send(sock, "watchdog", "blank", NODE_NAME);

  while(true){
    variableList = Msg_Handler(variableList, variableNameList,sock);

    state = variableList[0];       

  }   

return 0;
}