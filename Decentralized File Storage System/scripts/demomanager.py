#!/usr/bin/env python3
# inspired by lab3's `launch.py`
import json
import random
import socket
import sys
import time
from paramiko import SSHClient, AutoAddPolicy

# Project-specific configuration
PROJECT = "project-a-series-of-tubes"
CLASS = "csee4119-spring-2024"

# Fun with f-strings
REPO = f"{CLASS}/{PROJECT}"
REPO_ROOT = f"~/{PROJECT}"
REPO_URL = f"github.com:{REPO}.git"
TRACKER_PY = f"{REPO_ROOT}/blocktubes/tracker.py"
PEER_PY = f"{REPO_ROOT}/blocktubes/peer.py"

# User-specific configuration
MY_UNI = "rdn2108"
MY_KEY = "/Users/rdn/.ssh/csee4119-s24"
VM_IPS = ["35.239.66.54", "35.202.218.139", "34.172.121.79", "34.71.33.207"]
TRACKER = VM_IPS[0]
PEERS = VM_IPS[1:]

# Random port selection
MINPORT = 49152
MAXPORT = 65535
RANDOM_PORT = random.randint(MINPORT, MAXPORT)

# Port configuration
MAGIC_PORT = RANDOM_PORT

# or use a fixed port for testing
MAGIC_PORT = 55551

TRACKER_PORT = MAGIC_PORT - 1


def main():
    """Main function to run the demo."""
    try:
        info(f"Starting the demo with tracker: {TRACKER} and peers: {PEERS}")
        dm = DemoManager(MY_UNI, MY_KEY, TRACKER, PEERS)
        #dm.init_tracker(TRACKER_PORT)
        #dm.init_peers(MAGIC_PORT)
        # let `tmux.sh` handle the initialization

        # Command peers to mine
        dm.send_tcp_command_to_peers("mine", MAGIC_PORT)
        time.sleep(5)

        # Fetch blockchains from all peers
        dm.get_blockchains()

        # Check if all blockchains are identical
        timestamp_tolerance = 5
        if check_all_blockchains(dm, PEERS, timestamp_tolerance):
            print("Test Passed: All blockchains are consistent.")
        else:
            print("Test Failed: Inconsistent blockchains.")

    except Exception as e:
        warn(f"An error occurred during the demo: {str(e)}")


def check_all_blockchains(dm, peers, tolerance):
    """
    Checks all blockchains collected from peers to determine if they are all identical.

    Args:
        dm (DemoManager): The manager handling the blockchains.
        peers (list): List of peer addresses.
        tolerance (int): The timestamp tolerance for comparing blockchains.

    Returns:
        bool: True if all blockchains are identical, otherwise False.
    """
    try:
        first_blockchain = None
        for ip in peers:
            blockchain_json = dm.blockchains.get(ip, [None])[0]  # Safe access to the dictionary
            if blockchain_json:
                try:
                    blockchain = json.loads(blockchain_json)
                except json.JSONDecodeError:
                    warn(f"JSON parsing failed for blockchain data from {ip}")
                    continue  # Skip this peer due to parsing error

                if first_blockchain is None:
                    first_blockchain = blockchain  # Set the first blockchain for comparison
                elif not blockchains_are_identical(first_blockchain, blockchain, tolerance):
                    return False  # Return False as soon as a discrepancy is found
        return True if first_blockchain is not None else False  # Return False if no valid blockchain was found

    except Exception as e:
        warn(f"An error occurred during blockchain comparison: {str(e)}")
        return False  # Return False on any other errors

def blockchains_are_identical(first, new, tolerance):
    """
    Compares two blockchains to determine if they are identical.

    Args:
        first (dict): The first blockchain data structure.
        new (dict): The new blockchain data structure.
        tolerance (int): The allowed difference in timestamps.

    Returns:
        bool: True if the blockchains are identical, otherwise False.
    """
    if len(first["chain"]) != len(new["chain"]):
        return False

    for block1, block2 in zip(first["chain"], new["chain"]):
        if (block1["prev_hash"] != block2["prev_hash"] or
            block1["proof"] != block2["proof"] or
            block1["message"] != block2["message"] or
            abs(block1["unix_timestamp"] - block2["unix_timestamp"]) > tolerance):
            return False

    return True


class DemoManager:
    """A wrapper class for managing SSH connections to multiple hosts."""
    def __init__(self, username, key_path, tracker_ip, peer_ips):
        self.username = username
        self.key_path = key_path
        self.tracker_ip = tracker_ip
        self.peer_ips = peer_ips
        self.ssh_clients = {ip: self.create_ssh_client(ip) for ip in peer_ips + [tracker_ip]}
        info(f"Tracker IP: {tracker_ip}, Peer IPs: {peer_ips}")

    def create_ssh_client(self, ip):
        try:
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            # ssh_config = {"StrictHostKeyChecking": "no"}
            ssh.connect(ip, username=self.username, key_filename=self.key_path)
            # ssh.conenct(ip, username=self.username, key_filename=self.key_path, config=ssh_config)
            return ssh
        except Exception as e:
            warn(f"Failed to set up SSH client for IP {ip}: {e}")

    def close_all(self):
        for ssh in self.ssh_clients.values():
            ssh.close()

    def init_tracker(self, port):
        """Initialize the tracker on the specified port."""
        cmd = f"python3 {TRACKER_PY} {port}"
        self.execc(self.tracker_ip, cmd)

    def init_peers(self, port):
        """Initialize the peers on the specified port."""
        for i, ip in enumerate(self.peer_ips):
            cmd = f"python3 {PEER_PY} {self.tracker_ip} {port + i}"
            self.execc(ip, cmd)
            info(f"Peer initialized on {ip}:{port + i}")

    def execc(self, ip, command):
        """
        Executes a command on a remote host via SSH and logs the output or errors.

        Args:
            ip (str): The IP address of the remote host.
            command (str): The command to execute on the remote host.
        """
        command = f"nohup {command} > /dev/null 2>&1 &"
        info(f"Executing command '{command}' on {ip}")
        ssh = self.ssh_clients.get(ip)
        if ssh:
            try:
                stdin, stdout, stderr = ssh.exec_command(command)
                stderr_output = stderr.read().decode()
                if stderr_output:
                    warn(f"Error executing command '{command}' on {ip}: {stderr_output}")
                return stdout.read().decode()  # Optionally return output for further processing
            except Exception as e:
                warn(f"Failed to execute command on {ip}: {e}")
                return None

    def execc_in_all(self, command, ip_list):
        """
        Executes a command via SSH on all specified IPs and aggregates responses.

        Args:
            command (str): The command to execute on each remote host.
            ip_list (list): List of IP addresses to execute the command on.

        Returns:
            dict: A dictionary containing the responses from each IP.
        """
        responses = {}
        for ip in ip_list:
            if ip in self.ssh_clients:
                response = self.execc(ip, command)
                responses[ip] = response
        return responses

    def sync_vms(self):
        """Sync the project repo on all remote hosts."""
        cd_and_sync = f"[[ -d {REPO_ROOT} ]] && cd {REPO_ROOT} && git pull || git clone {REPO_URL} {REPO_ROOT}"
        setup_py = "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && export PYTHONPATH=$PYTHONPATH:$(pwd)"
        for ip in self.peer_ips + [self.tracker_ip]:
            full_command = f"nohup bash -c '{cd_and_sync}' > /dev/null 2>&1 &"
            self.execc(ip, full_command)
            full_command = f"nohup bash -c '{setup_py}' > /dev/null 2>&1 &"
            self.execc(ip, full_command)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()

    def send_tcp_command_to_peers(self, command, port, timeout=5):
        """
        Sends a TCP command to all peers on a specific port with error handling, socket reuse, and timeout.

        Args:
            command (str): The command to send to each peer.
            port (int): The port on which peers are listening for commands.
            timeout (int): Timeout for the TCP connection in seconds.

        Returns:
            dict: A dictionary with the IP as the key and a tuple (response, success) as the value.
        """
        cmd_port = port + 1000
        responses = {}
        info(f"Commanding all peers to: {command}")
        for ip in self.peer_ips:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.settimeout(timeout)
                    sock.connect((ip, cmd_port))
                    success(f"Connected to {ip}:{cmd_port}")
                    sock.sendall(command.encode())
                    response = sock.recv(4096).decode()
                    responses[ip] = (response, True)
                    info(f"TCP command '{command}' sent to {ip}:{cmd_port}, response: {response[:50]}")
                    cmd_port += 1  # Increment the port for the next peer
            except socket.timeout:
                responses[ip] = (None, False)
                info(f"Timeout occurred while sending TCP command to {ip}:{cmd_port}")
            except Exception as e:
                responses[ip] = (None, False)
                warn(f"Failed to send TCP command to {ip}:{cmd_port}: {e}")
                # TODO exit on error?
                sys.exit(1)


        return responses

    def get_blockchains(self):
        """Fetch the blockchains from all peers."""
        info("Fetching blockchains from all peers...")
        self.blockchains = {}
        self.blockchains = self.send_tcp_command_to_peers("get blockchain", MAGIC_PORT)
        # blockchains returned as "responses", a dictionary with IP as key and tuple (response, success) as value

def success(message):
    """Prints a success message to the console."""
    print("\033[92mSuccess: " + message + "\033[0m", file=sys.stderr)

def info(message):
    """Prints an info message to the console."""
    print("\033[94mInfo: " + message + "\033[0m", file=sys.stderr)

def warn(message):
    """Prints a warning message to the console."""
    print("\033[91mWarning: " + message + "\033[0m", file=sys.stderr)

if __name__ == "__main__":
    main()
