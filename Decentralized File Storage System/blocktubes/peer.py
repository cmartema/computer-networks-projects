import argparse
import json
import logging
import socket
import threading
import time
from typing import Optional

from blocktubes.blockchain import Block, BlockChain

from blocktubes.logger import block_logger

BUFSIZE = 4096  # constant buffer size for sockets


def init_UDP_listening_socket(port):
    """
    Initialize a UDP socket to listen for broadcasts on the given port.

    Args:
    port (int): The port number to listen on.

    Returns:
    socket: The created socket object. None on error.
    """
    try:
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("", port))
        return listen_socket
    except socket.error as e:
        block_logger.exception(f"Error creating UDP socket: {e}")
        return None


class Peer:
    """A peer in a P2P network."""

    def __init__(self, port, tracker_host, tracker_port):
        """Initialize the peer and register with the tracker."""
        self.id = (socket.gethostbyname(socket.gethostname()), port)
        self.peers = set()
        self.lock = threading.Lock()
        self.blockchain = BlockChain(hash_difficulty=3)
        self.register_with_tracker(tracker_host, tracker_port)
        self.listen_socket = init_UDP_listening_socket(port)
        self.command_port = port + 1000  # Use a different port for command handling
        # TODO graceful shutdown on error?

    def start(self):
        threading.Thread(target=self.command_listener, daemon=True).start()
        threading.Thread(target=self.listen_for_broadcasts, daemon=True).start()
        block_logger.info("Peer registered! Listening for broadcasts.")

    def register_with_tracker(self, tracker_host, tracker_port):
        """
        Register the peer with the tracker by sending a JSON-encoded packet.

        Args:
        tracker_host (str): The hostname of the tracker.
        tracker_port (int): The port number of the tracker.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect((tracker_host, tracker_port))
                sock.sendall(self.packet())
                response = sock.recv(BUFSIZE)
                if response:
                    block_logger.info(
                        f"Received response from tracker: {response.decode()}"
                    )
        except socket.error as e:
            block_logger.exception(f"Error registering with tracker: {e}")

    def packet(self):
        """Return the peer's ID as a JSON-encoded packet."""
        return json.dumps({"host": self.id[0], "port": self.id[1]}).encode()

    def __str__(self):
        formatted_string = f"{self.id[0]}:{self.id[1]} - Peers: "
        with self.lock:
            for peer in self.peers:
                formatted_string += f"{peer} "
        return formatted_string

    def handle_broadcast(self, data: str):
        try:
            self.handle_received_data(data)
        except json.JSONDecodeError as e:
            block_logger.exception(f"Error decoding broadcast data: {e}")
        except TypeError as e:
            block_logger.exception(f"Data handling error: {e}")

    def send_data_to_peers(self, data: str):
        for peer in self.peers:
            self.send_data_to_peer(data, peer)

    def broadcast_new_block(self, block):
        data = json.dumps({"type": "new_block", "block": block.__dict__})
        self.send_data_to_peers(data)

    def request_blockchain_broadcast(self):
        data = json.dumps({"type": "blockchain_broadcast_request"})
        self.send_data_to_peers(data)

    def send_data_to_peer(self, data, peer):
        try:
            block_logger.info(f"Sending data to peer: {data}, {peer}")
            host, port = peer  # Ensure peer is unpacked correctly
            port = int(port)  # Ensure port is an integer
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(data.encode(), (host, port))
        except socket.error as e:
            block_logger.exception(f"Error sending data to peer {peer}: {e}")
        except ValueError as e:
            block_logger.exception(f"Data unpacking error: {e}, with peer data: {peer}")

    def handle_received_data(self, data: str):
        message = json.loads(data)
        if message["type"] == "new_block":
            block = Block(**message["block"])
            if self.blockchain.validate_and_add_block(block):
                block_logger.info("Block added to the blockchain")
            else:
                block_logger.info(
                    "Received invalid block. Requesting blockchain rebroadcast"
                )
                self.request_blockchain_broadcast()
        elif message["type"] == "blockchain":
            received_chain = [Block(**block_data) for block_data in message["chain"]]
            if self.blockchain.is_valid_chain(received_chain):
                if len(received_chain) > len(self.blockchain.chain):
                    self.blockchain.chain = received_chain
                    block_logger.info(
                        "Replaced local blockchain with longer valid chain"
                    )
                elif len(received_chain) == len(self.blockchain.chain):
                    if (
                        received_chain[-1].unix_timestamp
                        > self.blockchain.chain[-1].unix_timestamp
                    ):
                        self.blockchain.chain = received_chain
                        block_logger.info(
                            "Replaced local blockchain with a chain with a newer timestamp"
                        )
        elif message["type"] == "peers_update":
            manifest = {tuple(peer) for peer in message["peers"]}
            manifest.discard(self.id)
            self.peers.update(manifest)
            block_logger.info(f"Updated peers: {self.peers}")
        elif message["type"] == "blockchain_broadcast_request":
            self.broadcast_blockchain()
        else:
            block_logger.error(f"Received unknown message type: {message=}")

    def mine_and_broadcast_block(self, message: str) -> Optional[Block]:
        block = self.blockchain.mine_block(message)
        if block:
            self.broadcast_new_block(block)
            self.broadcast_blockchain()
        return block

    def broadcast_blockchain(self):
        data = json.dumps(
            {
                "type": "blockchain",
                "chain": [block.__dict__ for block in self.blockchain.chain],
            }
        )
        for peer in self.peers:
            self.send_data_to_peer(data, peer)

    def listen_for_broadcasts(self):
        try:
            while True:
                data, addr = self.listen_socket.recvfrom(BUFSIZE)
                self.handle_broadcast(data.decode())
        except socket.error as e:
            block_logger.exception(f"Failed to receive broadcast: {e}")
        finally:
            self.listen_socket.close()

    def command_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("", self.command_port))
            server_socket.listen()
            block_logger.info(f"Command listener active on port {self.command_port}")

            while True:
                try:
                    client_socket, _ = server_socket.accept()
                    with client_socket:
                        command = client_socket.recv(BUFSIZE).decode().strip()
                        block_logger.info(f"Recieved command: {command=}")
                        if command == "mine":
                            block = self.mine_and_broadcast_block(
                                "This is a test block."
                            )
                            client_socket.sendall(
                                b"Block mined and broadcasted\n"
                                if block
                                else b"Failed to mine block\n"
                            )
                        elif command == "get blockchain":
                            response = json.dumps(
                                {
                                    "type": "blockchain",
                                    "chain": [
                                        block.__dict__
                                        for block in self.blockchain.chain
                                    ],
                                }
                            )
                            client_socket.sendall(response.encode())
                except Exception as e:
                    block_logger.exception(f"Error handling command: {e}")

    def run(self):
        """Start listening for broadcasts, register with tracker, and print peers."""
        self.start()
        try:
            while True:
                block_logger.info(self)
                time.sleep(5)
        except KeyboardInterrupt:
            block_logger.info("Keyboard Interrupt detected. Shutting down peer.")
            self.shutdown()

    def shutdown(self):
        """Close the listening socket and print a shutdown message."""
        block_logger.info("Shutting down peer.")
        self.listen_socket.close()
        block_logger.info("Closed UDP socket.")

def main():
    parser = argparse.ArgumentParser(description="Start a peer connection to tracker.")
    parser.add_argument("port", type=int, help="Port number for this peer")
    parser.add_argument(
        "--tracker_host", help="Hostname of the tracker", default="localhost"
    )
    parser.add_argument(
        "--tracker_port", type=int, help="Port number of the tracker", default=50_000
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(message)s", level=logging.INFO)
    peer = Peer(args.port, args.tracker_host, args.tracker_port)
    peer.run()

if __name__ == "__main__":
    main()
