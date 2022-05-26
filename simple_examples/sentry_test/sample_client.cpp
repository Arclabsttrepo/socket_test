#include "cppclient.h"
#define NODE_NAME "client5"
#define PORT 5050
#define SERVER "127.0.1.1"

int port = 5050;
char * server = "127.0.1.1";



int main(){

    int sock = connect(PORT, SERVER);
    Send(sock, "watchdog", "blank", NODE_NAME);

    while(true){

        json testobj = Receive(sock);
        std::cout << testobj <<std::endl;
    }   

  

return 0;
}