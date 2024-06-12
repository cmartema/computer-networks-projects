[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/sJyArgKF)
# CSEE 4119 Spring 2024, Assignment 3
## Cristopher Marte Marte (cjm2301)
## Github Username: cmartema

*Please replace this text with information on how to run your code, description of each file in the directory, and any assumptions you have made for your code*


# Distance Vector Routing (DVR) Program

This program announces its routing table to its neighbors and updates its routing table based on the received routing tables from its neighbors.

## Setup

1. Configure the [`topology.dat`] file to set up the network topology. Each line contains two nodes and their cost, separated by a space. Please use the external IP of each Google cloud VM. Make sure all VMs use the same topology file.

2. Edit the [`launch.py`] file and replace `<path_to_your_ssh_key>` with the path to your SSH key locally. You may need to use an absolute path and avoid using "~" to denote your home directory. Also replace `<external_IPs_of_your_VMs>` with the external IPs of your VMs, as a list of strings.

## Running the Program

You can run the project with the following command:

```sh
python3 launch.py
```

Alternatively, you can run the network overlay for each VM with the following commands:

```sh
chmod +x ./overlay
./overlay <overlay_port> <internal_port> <topology_file>&
```
And open another terminal and run the following command when all of the VMs are ready for the connection:

```
python3 dvr.py <overlay_port>
```

## Program Description

Once the overlay has finished setting up, you will see the phrase "waiting for connection from the network process...". Then, you will connect to the overlay in the local machine through the overlay port (default 60000).

The program parses the `topology.dat` file to retrieve the total number of nodes in the network and your neighbors with the corresponding cost.

Any message sent to the overlay will be broadcasted to the neighbors only. The program keeps announcing the table to the neighbors and updates its own table based on the received routing tables.

The routing table is logged at the initial state, and whenever it is updated using the following format:

```
<neighbor_1>:<cost_1>:<next_hop_1> ... <neighbor_n>:<cost_n>:<next_hop_n>
```

The log file is saved to `log_<internal_ip>.txt`.

For example, for `log_10.128.0.2.txt`:

```
<10.128.0.3>:7:<10.128.0.3> <10.128.0.4>:2:<10.128.0.4>
<10.128.0.3>:5:<10.128.0.4> <10.128.0.4>:2:<10.128.0.4>
```

## dvr.py

This is the main script for the Distance Vector Routing (DVR) program. It manages a routing table for a node in a network and communicates with its neighbors to update the routing table.

### Key Components

- **RoutingTable Class**: This class manages a routing table for a node. It has methods to print the table, get the distance vector (DV), update the routing table, and log the DV table to a file.

- **connect_to_overlay Function**: This function establishes a TCP connection to a network overlay running on the local machine.

- **send_dvr Function**: This function sends the current node's distance vector (DV) table to its neighbors.

- **receive_dvr Function**: This function receives a distance vector (DV) table from a neighbor node.

### How it operates

1. The script starts by parsing the `topology.dat` file to retrieve the total number of nodes in the network and the neighbors with their corresponding cost.

2. It then initializes a [`RoutingTable`]object with the neighbors table, total number of nodes, and the internal IP of the current VM.

3. The script connects to the network overlay using the `connect_to_overlay` function.

4. In an infinite loop, the script sends its DV table to its neighbors using the `send_dvr`function, receives DV tables from its neighbors using the `receive_dvr` function, and sleeps for 5 seconds.

You can run the script with the following command:

```sh
python3 dvr.py <overlay_port>
```

Where `<overlay_port>` is the port used to send messages to neighbors.

For more details, please refer to the `dvr.py` file.

## Note

Due to the UI that converts the IP addresses to alphabet for easier display in the `dvr.py` file, you are only allowed to use less than the amount of the letters of alphabet amount of nodes.