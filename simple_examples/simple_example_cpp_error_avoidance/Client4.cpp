// Client side C/C++ program to demonstrate Socket
// programming
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <iostream>
#include <algorithm>
#include <string>
#include "newconversioncpp.h"
#define PORT 5050
#define HEADER_SIZE 13
#define NODE_NAME "client4"
#define DCONN_MSG "DISCONNECT!"

/*Gets length of the message to be sent, Stores the length in a HEADER,
Fills the HEADER with blank spaces to meet the set HEADER_SIZE,
Sends the HEADER message to the server and then sends the actual message
to the server.
*/
int Client_Send(int sock, json nodeName, json id, json msg){
	std::string jsonMsg;
	jsonMsg = Convert_to_json(nodeName, id, msg);
	int n = jsonMsg.length();
    // declaring character array
    char char_array[n + 1];
    // copying the contents of the string to char array
    strcpy(char_array, jsonMsg.c_str());
	//stores the HEADER message
    char temp[HEADER_SIZE] = "";
    int msgLength, lengthVal = 0;
    std::string sendLength = "";
	//stores the length of the actual message in msgLength. 
    msgLength = strlen(char_array);
	//converts the message length to a string to get the length of 
	//the integer value.
    sendLength = std::to_string(msgLength);
    lengthVal = sendLength.length();
	//Writes the header delimiter to the beginning of the HEADER,
	//by individually assigning each char to the HEADER.
    temp[0]='[';
	temp[1]='|';
	temp[2]=']';
	// Add padding to the HEADER message to fill to the size of
	// HEADER_SIZE.
	for(int x = 3; x < (HEADER_SIZE); x++){
         temp[x] = '`'; //pad
     }
	int i=0;
	// Add the length of the message by overwritting some of the padding
	for(int x = 3; x < lengthVal+3; x++){
        temp[x] = sendLength[i];
		i++;
    }
	//Starting from the (last stored char + 1) to the (HEADER_SIZE - 1), 
	//the HEADER message is filled with spaces to ensure the server
	//reads only the header message initially.
     
	 for (int x=0; x<(HEADER_SIZE); x++){
	 	std::cout<<temp[x]; 
	 }
	 std::cout<<std::endl;

	 for (int x=0; x!=msgLength; x++){
	 	std::cout<<char_array[x]; 
	 }
	std::cout<<std::endl;
	//Sends the HEADER message to the server, so that the server knows
	//the length of the actual incoming message.
    send(sock,temp, strlen(temp), 0);
	//Sends the actual message to the server.
    send(sock, char_array, strlen(char_array), 0);
}

/*
Receives the HEADER message from the server, stores the actual message
length in msgLength. If the HEADER message is received, then prepare
to receive the actual message with the no. of bytes to be received set
to msgLength.
*/
void Client_Recv(int sock){
	int msgLength = 0;
	int valRead = 0;
	int msgRead = 0;
	char header[HEADER_SIZE];
	std::string headerMsg;
	char servMsg[1024];
	if (msgLength == 0){
		//Receives the HEADER message from the server and stores the
		//message in header, with the number of bytes received set to 
		//HEADER_SIZE.
		valRead = recv(sock, header, HEADER_SIZE, 0);

		headerMsg = header;
		headerMsg.erase(std::remove(headerMsg.begin(), headerMsg.end(),'`'), headerMsg.end());
		headerMsg.erase(std::remove(headerMsg.begin(), headerMsg.end(),'['), headerMsg.end());
		headerMsg.erase(std::remove(headerMsg.begin(), headerMsg.end(),'|'), headerMsg.end());
		headerMsg.erase(std::remove(headerMsg.begin(), headerMsg.end(),']'), headerMsg.end());

		//Converts the HEADER message from a char array to an integer.
		msgLength = std::stoi(headerMsg);
	}
	if (msgLength > 0){
		//If the HEADER  message is received, then receive the actual 
		//message from the server and store in servMsg, with the number
		//of bytes to be received set as msgLength.
		msgRead = recv(sock, servMsg, msgLength, 0);
		std::cout << strlen(servMsg) << std::endl;
		std::cout << servMsg << std::endl;
        json object = Json_to_object("words");
        //std::cout << object << std::endl;
	}


	// if(header){
	// 	msgRead = recv(sock, servMsg, msgLength, 0);
	// 	std::cout << strlen(servMsg) << std::endl;
	// 	std::cout << servMsg << std::endl;
	// }
	else{
		return;
	}

}


int main(int argc, char const* argv[])
{
	int sock = 0, valread;
	char header[HEADER_SIZE] = "[|]3````````";
	std::string headerMsg = "";
	int msgLength = 0;
	struct sockaddr_in serv_addr;
	json arraytest = json::array();
	
	//std::string attempt="{\"key\": \"client2\", \"msg\": \"Hello from client1\", \"timestamp\": 1651691756.8724802, \"type\": \"str\"}";
	std::string attempt = "not johnathan";
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
	if (inet_pton(AF_INET, "127.0.1.1", &serv_addr.sin_addr)
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
	
	Client_Send(sock, "watchdog", "blank", NODE_NAME);
	/*while (true){
    	Client_Send(sock, "client2", attempt);
	}*/
	json keyarray = json::array();
	keyarray = {"client3", "client3"};
	json idarray = json::array();
	idarray = {"topic","topic2"};
	json msgarray = json::array();
	msgarray = {attempt, "not carl"};
    Client_Send(sock, keyarray, idarray, msgarray);
	printf("Hello message sent\n");
	Client_Recv(sock);
	return 0;
}
