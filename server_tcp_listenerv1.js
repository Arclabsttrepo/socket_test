/*https://www.yld.io/blog/building-a-tcp-service-using-node-js/
Description: Node.js server script that listens to tcp socket on the selected port.

Run service from terminal:
Navigate to folder where file is stored:
$ node server_tcp_listener.js

On a different terminal window you can then connect to our server using a 
command-line application like Telnet or Netcat:
$ nc localhost 9000  
*/

//The net module provides an asynchronous network API for creating 
//stream-based TCP or IPC servers (net.createServer()) and clients 
var net = require('net');

//creating the server object by calling .createServer on the net module. 
//This gives us a server object
var server = net.createServer();

//execute handleConnection function (written below)
server.on('connection', handleConnection);

//listen to port xxxx = 9000
server.listen(9000, function() {    
  console.log('server listening to %j', server.address());  
});

/* Bind the handleConnection function to the connection event.
connection events: a data event every time data arrives from the connected peer,
                   a close event once that connection closes, 
                   an error event if an error happens on the socket. */
function handleConnection(conn) {
  //get address of connecting client      
  var remoteAddress = conn.remoteAddress + ':' + conn.remotePort;  
  console.log('new client connection from %s', remoteAddress);

  
  /*The connection passes raw buffers when emitting data events.
  //Set encoding of incoming data to utf-8 so that string data 
  is emitted rather than raw buffers */
  conn.setEncoding('utf8');
  conn.on('data', onConnData);  
  conn.once('close', onConnClose);  
  conn.on('error', onConnError);

  //emits a data event every time data arrives from the connected peer
  function onConnData(d) {  
    console.log('connection data from %s: %j', remoteAddress, d);
    //send the received data back to the client on the port
    conn.write(d);
    
    var http = require('http');
    //create a server object:
    http.createServer(function (req, res) {
    res.write(d); //write data response to the webpage
    res.end(); //end the response
    }).listen(8080); //the server object listens on port 8080
    // go to http://localhost:8080/ to view data
  }

  //emits close event once that connection closes
  function onConnClose() {  
    console.log('connection from %s closed', remoteAddress);  
  }

  //emits an error event if an error happens on the socket
  function onConnError(err) {  
    console.log('Connection %s error: %s', remoteAddress, err.message);  
  }  
}