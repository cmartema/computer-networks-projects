[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/7VnFugBz)

# CSEE 4119 Spring 2024, Assignment 1
## Cristopher Marte Marte
## GitHub username: cmartema



===========================================================

# README: Network Simulation and Video Streaming Application

===========================================================

1. Description:
---------------
This project consists of three Python scripts: `client.py`, `server.py`, and `network.py`. Together, they simulate a basic video streaming application over a network connection, where the client requests video chunks from the server and adapts the streaming quality based on estimated network conditions.

2. Usage Instructions:
-----------------------
- To run the application, follow these steps:

    a. Ensure you have Python 3.x installed on your system.
    
    b. Open a terminal or command prompt.
    
    c. Start the server by running the command:
       ```
       python3 server.py <listen_port>
       ```
       Replace `<listen_port>` with a port number in the range of 49152 to 65535.

    d. Start the network simulation by running the command:
       ```
       python3 network.py <networkPort> <serverAddr> <serverPort> <bwFileName> <latency>
       ```
       Replace `<networkPort>`, `<serverAddr>`, `<serverPort>`, `<bwFileName>`, and `<latency>` with appropriate values.

    e. Finally, start the client by running the command:
       ```
       python3 client.py <network_addr> <network_port> <name> <alpha>
       ```
       Replace `<network_addr>`, `<network_port>`, `<name>`, and `<alpha>` with appropriate values.
       
3. Assumptions:
----------------
- The scripts assume that the video files (chunks and manifest file) are available on the server and accessible to the client upon request.
- Bandwidth information is provided in a file specified by `<bwFileName>`, with each line indicating the available bandwidth at a specific time.
- Latency (`<latency>`) represents the delay in the network link.
- The client dynamically adjusts streaming quality based on estimated network throughput.

4. Corner Cases:
-----------------
- Ensure that all necessary video files, including the manifest file and video chunks, are available in the expected directory structure on the server.
- The application assumes a stable network connection during streaming. Sudden network disruptions or high latency may affect streaming quality.
- Input validation is minimal in the provided scripts. Ensure that inputs are correctly formatted to prevent errors.

5. Incomplete Aspects:
------------------------
- Error handling and recovery mechanisms in case of network failures or file not found scenarios are rudimentary and may need improvement.
-

