// Client side C/C++ program to demonstrate Socket
// programming
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <iostream>
//#include "nlohmann/json.hpp"
#define PORT 5050
#define HEADER_SIZE 64


/*Gets length of the message to be sent, Stores the length in a HEADER,
Fills the HEADER with blank spaces to meet the set HEADER_SIZE,
Sends the HEADER message to the server and then sends the actual message
to the server.
*/
int Client_Send(int sock, char *buf){
	//stores the HEADER message
    char temp[HEADER_SIZE] = "";
    int msgLength, lengthVal = 0;
    std::string sendLength = "";
	//stores the length of the actual message in msgLength. 
    msgLength = strlen(buf);
	//converts the message length to a string to get the length of 
	//the integer value.
    sendLength = std::to_string(msgLength);
    lengthVal = sendLength.length();
	//Writes the length of the message to the beginning of the HEADER,
	//by individually assigning each char to the HEADER from sendLength
    for(int x = 0; x < lengthVal; x++){
        temp[x] = sendLength[x]; 
    }
	//Starting from the (last stored char + 1) to the (HEADER_SIZE - 1), 
	//the HEADER message is filled with spaces to ensure the server
	//reads only the header message initially.
     for(int x = lengthVal; x < (HEADER_SIZE); x++){
         temp[x] = ' ';
     }
	//Sends the HEADER message to the server, so that the server knows
	//the length of the actual incoming message.
    send(sock,temp, strlen(temp), 0);
	//Sends the actual message to the server.
    send(sock, buf, strlen(buf), 0);
}

/*
Receives the HEADER message from the server, stores the actual message
length in msgLength. If the HEADER message is received, then prepare
to receive the actual message with the no. of bytes to be received set
to msgLength.
*/
void Client_Recv(int sock){
	int msgLength, valRead, msgRead = 0;
	char header[HEADER_SIZE];
	char servMsg[1024];
	//Receives the HEADER message from the server and stores the
	//message in header, with the number of bytes received set to 
	//HEADER_SIZE.
	valRead = recv(sock, header, HEADER_SIZE, 0);
	//Converts the HEADER message from a char array to an integer.
	msgLength = std::strtol(header, nullptr, 10);
	//If the HEADER  message is received, then receive the actual 
	//message from the server and store in servMsg, with the number
	//of bytes to be received set as msgLength.
	if(header){
		msgRead = recv(sock, servMsg, msgLength, 0);
		std::cout << strlen(servMsg) << std::endl;
		std::cout << servMsg << std::endl;
	}
	else{
		return;
	}

}

int main(int argc, char const* argv[])
{
	int sock = 0, valread;
	struct sockaddr_in serv_addr;
	char* hello = "{\"message\":\"l\"}";
    //Message written in JSON-like format for testing.
    char* fullmsg = "{\"key\": \"client2\", \"msg\": \"Hello from client1\", \"timestamp\": 1651691756.8724802, \"type\": \"str\"}";

	//Creates the client socket with domain as IPv4 protocol,
	//type as TCP/IP and the protocol set to the default.
	//The if statement checks for errors in creating the socket. 
    if((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0){
		std::cout << "\n Socket creation error! \n";
		return -1;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(PORT);

	//Convert IPv4 and IPv6 addresses from text to binary form.
	if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)
		<= 0) {
		printf(
			"\nInvalid address/ Address not supported \n");
		return -1;
	}

	//Initiates a connection on the socket at the server address and
	//performs an error check.
	if (connect(sock, (struct sockaddr*)&serv_addr,
				sizeof(serv_addr))
		< 0) {
		printf("\nConnection Failed \n");
		return -1;
	}
	//hello = "Hello from the client and his friend JSON";
    Client_Send(sock, fullmsg);
	printf("Hello message sent\n");
	//Client_Recv(sock);
	return 0;
}
