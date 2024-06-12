import json
import socket
import threading
import time
from blocktubes.peer import Peer
from blocktubes.tracker import Tracker

# Configuration variables
TRACKER_PORT = 55355
BASE_PEER_PORT = 54321
NUM_PEERS = 4
TRACKER_HOST = "127.0.0.1"  # Typically localhost for testing

def run_tracker(port):
    tracker = Tracker(port)
    print(f"Starting tracker at port {port}...")
    tracker.run()

def run_tracker_tread(port):
    tracker_thread = threading.Thread(target=run_tracker, args=(port,))
    tracker_thread.start()
    return tracker_thread

def run_peer(port, tracker_host, tracker_port):
    my_peer = Peer(port, tracker_host, tracker_port)
    print(f"Starting peer at port {port}...")
    my_peer.run()

def run_peer_thread(port, tracker_host, tracker_port):
    peer_thread = threading.Thread(target=run_peer, args=(port, tracker_host, tracker_port))
    peer_thread.start()
    return peer_thread

def start_peer_threads():
    peer_threads = []
    for i in range(NUM_PEERS):
        port = BASE_PEER_PORT + i
        peer_threads.append(run_peer_thread(port, TRACKER_HOST, TRACKER_PORT))
    return peer_threads

def send_command_to_peer(port, command):
    """Sends a command to a peer via TCP socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", port + 1000))  # Assuming command port is peer port + 1000
        sock.sendall(command.encode())
        response = sock.recv(4096).decode()
    return response

def main():
    # Start the tracker
    tracker_thread = run_tracker_tread(TRACKER_PORT)
    time.sleep(2)  # Allow the tracker to initialize

    # Start the peers
    peer_threads = start_peer_threads()
    time.sleep(2)  # Allow each peer to initialize and register with the tracker

    try:
        # Send command to mine a block to each peer
        for i in range(NUM_PEERS - 1):
            port = BASE_PEER_PORT + i
            print(f"Commanding peer at port {port} to mine a block...")
            send_command_to_peer(port, "mine")
            time.sleep(1)  # Stagger commands slightly

        # Fetch and compare the blockchains from each peer
        print("Fetch and compare the blockchains from each peer.")
        first_blockchain = None
        consistent = True
        timestamp_tolerance = 5  # Tolerance for timestamp differences in seconds

        for i in range(NUM_PEERS):
            port = BASE_PEER_PORT + i
            blockchain_json = send_command_to_peer(port, "get blockchain")
            blockchain_data = json.loads(blockchain_json)
            print(f"Blockchain from peer at port {port}: {blockchain_data}")

            if i == 0:
                first_blockchain = blockchain_data
            else:
                for j in range(len(first_blockchain["chain"])):
                    if j >= len(blockchain_data["chain"]):
                        consistent = False
                        break

                    block1 = first_blockchain["chain"][j]
                    block2 = blockchain_data["chain"][j]

                    if (
                        block1["prev_hash"] != block2["prev_hash"]
                        or block1["proof"] != block2["proof"]
                        or block1["message"] != block2["message"]
                        or abs(block1["unix_timestamp"] - block2["unix_timestamp"]) > timestamp_tolerance
                    ):
                        consistent = False
                        break

        if consistent:
            print("Test Passed: All blockchains are consistent.")
        else:
            print("Test Failed: Inconsistent blockchains.")

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Terminating...")

    finally:
        # Gently signal all threads to close if needed
        print("Stopping all peers and tracker...")
        for peer_thread in peer_threads:
            peer_thread.join()
        tracker_thread.join()
        print("All processes stopped.")

if __name__ == "__main__":
    main()

