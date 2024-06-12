import argparse
import json
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

BACKLOG = 10  # Maximum number of pending connections
BUFSIZE = 1024  # Buffer size for receiving data


def init_TCP_registration_socket(port):
    """
    Initialize a TCP socket for peer registration.
    Using TCP for registration guarantees that the tracker receives the registration.

    Args:
    port (int): The port number to listen on.

    Returns:
    socket: The created (TCP) socket object. None on error.
    """
    try:
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("", port))
        listen_socket.listen(BACKLOG)
        return listen_socket
    except socket.error as e:
        print("Error creating TCP socket:", e)
    return None


def init_UDP_broadcast_socket():
    """
    Initialize a UDP socket for broadcasting.

    Returns:
    socket: The created (UDP) socket object. None on error.
    """
    try:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return broadcast_socket
    except socket.error as e:
        print("Error creating broadcast socket:", e)
        return None


class Tracker:
    """A tracker for a P2P network."""

    def __init__(self, port, max_workers=BACKLOG):
        """Initialize the tracker with the given port."""
        self.port = port
        self.peers = set()  # (host, port) tuples of registered peers
        self.lock = threading.Lock()
        self.broadcast_socket = init_UDP_broadcast_socket()
        self.listen_socket = init_TCP_registration_socket(port)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def packet(self):
        """The encoded json packet to send to peers."""
        return json.dumps({"type": "peers_update", "peers": list(self.peers)}).encode()

    def send_packet(self, peer):
        """Send the peers list to a specific peer."""
        try:
            host, port = peer
            self.broadcast_socket.sendto(self.packet(), (host, port))
        except ValueError:
            print(f"Invalid port number: {port} for host {host}")
        except socket.error as e:
            print(f"Failed to send to {peer}: {e}")

    def broadcast_peers_to_peers(self):
        """Send the peers list to every peer."""
        while True:
            with self.lock:
                for peer in self.peers:
                    self.send_packet(peer)
            time.sleep(5)

    def handle_connection(self, connection, address):
        """Handle peer registration via TCP connection."""
        try:
            data = json.loads(connection.recv(BUFSIZE).decode())
            if data:
                print(f"Received registration: {data} from {address}")
                with self.lock:
                    self.peers.add((data["host"], int(data["port"])))
                connection.sendall(b"OK!")
            else:
                print(f"Failed to receive registration from {address}")
        except json.JSONDecodeError:
            print("Received invalid JSON data.")
            connection.sendall(b"Registration failed: Invalid data format.")
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            connection.close()

    def run(self):
        """
        Run the tracker. One thread broadcasts the list of peers to all
        peers. In the main loop, the tracker listens for incoming connections
        and utilizes a thread pool to handle each connection.
        """
        threading.Thread(target=self.broadcast_peers_to_peers, daemon=True).start()
        print(f"Tracker is broadcasting. Now listening for connections on port {self.port}...")

        try:
            while True:
                connection, address = self.listen_socket.accept()
                self.executor.submit(self.handle_connection, connection, address)
        except KeyboardInterrupt:
            print("Tracker interrupted by KeyboardInterrupt")
        except Exception as e:
            print(f"Tracker interrupted by exception: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
        finally:
            print("Exiting the main loop...")
            self.shutdown()

    def shutdown(self):
        """Shut down the thread pool and all sockets."""
        print("Shutting down thread pool...")
        self.executor.shutdown(wait=True)
        print("Closing sockets...")
        if self.broadcast_socket:
            self.broadcast_socket.close()
        if self.listen_socket:
            self.listen_socket.close()
        print("Tracker shutdown successfully.")


def main():
    parser = argparse.ArgumentParser(description="Start a tracker for a P2P network.")
    parser.add_argument("port", type=int, help="Port number for the tracker")
    args = parser.parse_args()
    tracker = Tracker(args.port)
    tracker.run()

if __name__ == "__main__":
    main()
