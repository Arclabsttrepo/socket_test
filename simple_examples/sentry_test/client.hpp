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
#include <chrono>
#include "conversion.hpp"

#define HEADER_SIZE 13
#define NODE_NAME "default"
#define DCONN_MSG "DISCONNECT!"

/*Gets length of the message to be sent, Stores the length in a HEADER,
Fills the HEADER with blank spaces to meet the set HEADER_SIZE,
Sends the HEADER message to the server and then sends the actual message
to the server.
*/
void Send(int sock, json nodeName, json id, json msg){
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
	//Sends the HEADER message to the server, so that the server knows
	//the length of the actual incoming message.
    send(sock,temp, strlen(temp), 0);
	//Sends the actual message to the server.
    send(sock, char_array, strlen(char_array), 0);
}
//Sends data to a specified client.
void Push(int sock, json nodeName, json id, json msg){
	Send(sock, nodeName, id, msg);
}

/*
Receives the HEADER message from the server, stores the actual message
length in msgLength. If the HEADER message is received, then prepare
to receive the actual message with the no. of bytes to be received set
to msgLength.
*/
json Receive(int sock){
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
		json object = Json_to_object(servMsg);
		
		return object;
	}
}

int connectClient(int port, char* server){
    int sock = 0;
    struct sockaddr_in serv_addr;
    //Creates the client socket with domain as IPv4 protocol,
	//type as TCP/IP and the protocol set to the default.
	//The if statement checks for errors in creating the socket. 
    if((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0){
		std::cout << "\n Socket creation error! \n";
		return -1;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(port);

	//Convert IPv4 and IPv6 addresses from text to binary form.
	if (inet_pton(AF_INET, server, &serv_addr.sin_addr)
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
	
    return sock;
}

/*
Handles incoming messages from the server. Ensures all the latest
data from expected sources is stored before returning latest data
to client. The last message received before returning latest data
is dependent on source with slowest data rate.
*/
json Msg_Handler(json variableList, json variableNameList, int sock){
	//A variable used to check if all the latest data is received.
	int dataReceived = 0;
	//A temporary array to store the latest data recevied from clients.
	json tempList = json::array();
	tempList = {};
	//A check to ensure the latest data from all expected clients is received.
	while(dataReceived != variableNameList.size()){
		//stores the message recevied from the server.
    	json receivedMsg = Receive(sock);
		//Compares the received message to the expected identifers
		//and stores the message in the appropriate array index.
        for(int x = 0; x < variableNameList.size(); x++){
            if(receivedMsg["identifier"]==variableNameList[x]){
                tempList[x] = receivedMsg; 
            }
		//Checks if the latest data from all expected messages is stored.	
        if (tempList.size()==variableNameList.size()){
            dataReceived = variableNameList.size(); 
        }
        }
    }
	variableList = tempList;
	return variableList;
}

