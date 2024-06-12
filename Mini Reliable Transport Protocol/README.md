[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/KQFw0QXH)
# CSEE 4119 Spring 2024, Assignment 2
## Cristopher Marte Marte (cjm2301)
## GitHub username: cmartema

# Mini Reliable Transport Protocol

This project implements a mini reliable transport protocol in Python. It includes features such as protection against segment losses via segment retransmissions, protection against data corruption via checksums, protection against out-of-order delivery of segments on the UDP layer, fast transmission for high latency scenarios, segmentation for large data transmission, and flow control to avoid overflowing receiver buffer. To simulate a lossy network condition between the client and server, we provided a network simulator (`network.py`) that opportunistically drops and corrupts segments based on a configuration file (`Loss.txt`). 

## How to Run the Code

1. Start the network simulator:

```sh
python3 network.py <networkPort> <clientAddr> <clientPort> <serverAddr> <serverPort> loss.txt
```

2. Start the server:

```sh
python3 app_server.py <server_port> <buffer_size>
```

3. Start the client:

```sh
python3 app_client.py <client_port> <network_addr> <network_port> <segment_size>
```

## File Descriptions

- [`network.py`]: Simulates the network. It forwards data between the server/client programs and varies the packet loss characteristics of the link between them.

- [`app_server.py`]: Implements a simple application server that uses MRT APIs to receive data. It listens for incoming connections, accepts one client, and receives 8000 bytes of data. It then compares the received data with the source file.

- [`app_client.py`]: A simple example application client that uses the MRT APIs to make a connection to the server and send a file.

- [`mrt_server.py`]: Defines server APIs of the mini reliable transport protocol.

- [`mrt_client.py`]: Defines client APIs of the mini reliable transport protocol.

- [`segmentClass.py`]: Contains the Segment class used for creating and handling segments.

- [`loss.txt`]: External file that varies link loss characteristics.

- [`data.txt`]: The file that the client sends to the server.

-  [`DESIGN.md`], [`TESTING.md`], [`README.md`]: Various documentation files.

## APIs

### Server side:

- Server.init(listen_port, receive_buffer_size): initialize the server

- Server.accept(): accept a client request

- Server.receive(conn, length): receive data over a given client connection

- Server.close(): close the current connection

### Client side:
- Client.init(client_port, server_addr, server_port, segment_size): initialize the client
- Client.connect(): connect to a given server
- Client.send(data): send a chunk of data over a given connection
- Client.close(): close the current connection

## Assumptions

- The network simulator is started before the server and client.

- The server is started before the client.

- The [`loss.txt`]file is correctly formatted and located in the same directory as the scripts.

- The [`data.txt`]file to be sent from the client to the server is located in the same directory as the scripts.

- The client and server scripts are run with the correct command line arguments as shown in the examples above.

- The system running the scripts has Python 3 installed.