import sys
import socket
import pickle
import time
import threading

class RoutingTable:
    """
    The RoutingTable class is used to manage a routing table for a node in a network.

    The class has the following methods:
    1.) print()
    2.) get_dv()
    3.) update_routing_table()
    4.) log_dv_table()
    """

    def __init__(self, table, num_nodes, my_ip):
        """
        Initializes the node with a given IP address, number of nodes, and a routing table.

        The method does the following:
        1. It creates a dictionary to map IP addresses to alphabet nodes.
        2. It creates a reverse mapping from alphabet nodes back to IP addresses.
        3. It prints the mapping of nodes to IP addresses.
        4. It initializes the routing table for the current node (identified by `my_ip`). The routing table is a dictionary where the keys are tuples of (destination, next hop) and the values are the costs of the routes. Initially, all costs are set to infinity.
        5. It updates the routing table with the initial costs and next hops provided in the `table` parameter. If a route from the `table` exists in the routing table, its cost is updated.
        """

        # Create a dictionary to map IP addresses to alphabet nodes
        nodes_alph = [chr(i) for i in range(ord('a'), ord('a') + len(num_nodes))]
        ip_addr = list(num_nodes)
        self.my_ip = my_ip
        self.node_map = dict(zip(ip_addr, nodes_alph))
        # Create a reverse mapping from alphabet nodes to IP addresses
        self.reverse_node_map = {v: k for k, v in self.node_map.items()}

        for ip_addr, node in self.node_map.items():
            print(f"Node {node} has IP address {ip_addr}")
        
        # Initialize the routing table for my_ip
        my_node = self.node_map[self.my_ip]
        nodes_alph.remove(my_node)  # Remove the current node from the list (no need to include it in the routing table)
        self.routing_table = {(dest, next_hop): float('inf') for dest in nodes_alph for next_hop in nodes_alph}
        for (dest, next_hop), cost in table.items(): # Update the routing table with the initial costs and next hops
            if (self.node_map[dest], self.node_map[next_hop]) in self.routing_table:
                self.routing_table[(self.node_map[dest], self.node_map[next_hop])] = cost
        self.print()
        sys.stdout.flush()
        self.log_dv_table()
            
    def print(self):
        """
        Prints the routing table.

        The method does the following:
        1. It groups the routes in the routing table by destination.
        2. It prints the node's name and its routing table.
        3. For each destination, it prints the cost and next hop for each route.
        4. If the cost is infinity, it prints '∞' instead of the cost.
        """
        routes_by_dest = {} # Group routes by destination
        for (dest, next_hop), cost in self.routing_table.items():
            if dest not in routes_by_dest:
                routes_by_dest[dest] = []
            routes_by_dest[dest].append((cost, next_hop))
        # Print each destination and its routes
        print(f"Distance Routing table for Node {self.node_map[self.my_ip]}")
        for dest, routes in routes_by_dest.items():
            print(f"to {dest}", end="\t")
            for cost, next_hop in routes:
                if cost == float('inf'):
                    print(f"(∞, via {next_hop})", end="\t")
                else:
                    print(f"({cost}, via {next_hop})", end="\t")
            print()
        print()
    
    def get_dv(self):
        """
        Returns the distance vector for the current node.

        The method does the following:
        1. It groups the routes in the routing table by destination.
        2. For each group of routes, it finds the route with the minimum cost.
        3. It creates a new distance vector table containing the minimum cost route for each destination.
        4. It returns the new distance vector table.
        """
        group = {}
        for (dest, next_hop), cost in self.routing_table.items():
            if dest not in group:
                group[dest] = []
            group[dest].append(((dest, next_hop), cost))
        dv_table = {min(costs, key=lambda x: x[1])[0]: min(costs, key=lambda x: x[1])[1] for costs in group.values()}
        return dv_table

    def update_routing_table(self, dv_table, ip_addr):
        """
        Updates the routing table based on the received distance vector (DV) table.

        The method takes two arguments:
        dv_table: The DV table received from a neighbor node.
        ip_addr: The IP address of the neighbor node that sent the DV table.

        The method does the following:
        1. It gets the current DV table.
        2. It calculates the new cost for each route in the received DV table.
        3. If the new cost is less than the current cost in the routing table, it updates the routing table and sets the updated flag to True.
        4. If the routing table is updated and the DV table has changed, it logs the new DV table, prints the new routing table, and flushes the standard output.
        """
        updated = False
        dv_before = self.get_dv()
        sender_node = self.node_map[ip_addr]
        for (dest, next_hop) in dv_table.keys():
            if (dest, next_hop) in self.routing_table:
                cost_to_sender = self.routing_table[sender_node, sender_node]
                #cost_to_sender = min(v for k, v in self.routing_table.items() if k[0] == sender_node)
                new_cost = dv_table[(dest, next_hop)] + cost_to_sender
                if new_cost < self.routing_table[(dest, next_hop)]:
                    self.routing_table[(dest, sender_node)] = new_cost
                    updated = True
        dv_after = self.get_dv()
        if updated and dv_before != dv_after:
            self.log_dv_table()
            print(f"Routing table updated by {sender_node}: ip_addr {ip_addr}")
            print(f"Updated DV for node {my_ip}: {dv_after}")
            self.print()
            sys.stdout.flush()

    def log_dv_table(self):
        """
        Logs the current node's distance vector (DV) table to a file. 

        The method retrieves the DV table, opens a file named "log_{self.my_ip}.txt" in append mode, 
        and writes each entry of the DV table in a specific format. If the cost is infinity, it's written as '∞'. 
        If there's no next hop, it's left blank. After writing all entries, it adds a newline character to separate 
        DV tables logged at different times.
        """
        dv_table = self.get_dv() # Get current dv table for
        with open(f"log_{self.my_ip}.txt", "a") as f:
                for (node, next_hop), cost in dv_table.items():
                    f.write(f"<{self.reverse_node_map[node]}>:{cost if cost != float('inf') else '∞'}:<{self.reverse_node_map[next_hop] if next_hop else ''}>")
                f.write("\n")


# Initialize neighbor table
neighbors_table = {} 

# Get the internal IP of the current VM
my_ip = socket.gethostbyname(socket.gethostname())
print(f"Internal IP: {my_ip}")


def connect_to_overlay(overlay_port):
    """
    The connect_to_overlay function is used to establish a TCP connection to a network overlay running on the local machine.

    The function takes one argument:

        - overlay_port: The port number on which the network overlay is listening for incoming connections.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', overlay_port))
    except Exception as e:
        print(f"Connecting overlay Error: {e}")
        return None
    return sock

def send_dvr(sock):
    """
    The send_dvr function sends the current node's distance vector (DV) table to its neighbors. 

    It takes one argument:

    sock: The socket object used for communication.
    """
    try:
        dv_table = rt.get_dv()
        content = (my_ip, dv_table)
        data = pickle.dumps(content, -1)
        sock.sendall(data)
    except Exception as e:
        print(f"Sending dv table Error: {e}")
        sys.stdout.flush()

def receive_dvr(sock): 
    """
    The receive_dvr function receives a distance vector (DV) table from a neighbor node.

    It takes one argument:

    sock: The socket object used for communication.
    """
    try:
        data = sock.recv(4096)
        if data:
            content = pickle.loads(data)
            ip_addr, dv_table = content
            sys.stdout.flush()
            rt.update_routing_table(dv_table, ip_addr)
    except Exception as e:
        print(f"receiving dv table Error: {e}")
        sys.stdout.flush()

# parse input arguments
# <overlay_port> 
# example: 60000
if __name__ == '__main__':
    overlay_port = int(sys.argv[1]) # the port used to send messages to neighbors
    elements = []

    #Parse the topology.dat file to retrieve the total number of nodes in the network and your neighbors with the corresponding cost
    with open("topology.dat", "r") as f:
        for line in f:
            try:
                tokens = line.strip().split()
                node1 = tokens[0]
                node2 = tokens[1]
                link_cost = int(tokens[2])
                elements.append(node1)
                elements.append(node2)
                total_num_nodes = list(dict.fromkeys(elements))
                if node1 == my_ip:
                    neighbors_table[(node2, node2)] = link_cost
                elif node2 == my_ip:
                    neighbors_table[(node1,node1)] = link_cost
            except ValueError as e:
                print(f"Invalid topology file format: {line} ({e})")

    rt = RoutingTable(neighbors_table, total_num_nodes, my_ip)
    sock = connect_to_overlay(overlay_port)
    sys.stdout.flush()
    while True:
        send_dvr(sock)
        receive_dvr(sock)
        time.sleep(5)













    
    
      
  