# import argparse
# import json
# commenting these out to quiet "unused" errors
import socket

commands = ["mine", "get blockchain"]
# These are assumed ports
peer_ports = [50_001, 50_002, 50_003]


def send_command(command: str, peer_port: int):
    # The command port offset is hardcoded in peer.py
    command_port = peer_port + 1000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_socket:
        send_socket.connect(("127.0.0.1", command_port))
        send_socket.send(command.encode())
