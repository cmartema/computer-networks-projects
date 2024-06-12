import socket
import os
import sys
import signal
import struct

def start_server(listen_port):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = ('localhost', listen_port)
    server_socket.bind(server)

    # Listen for incoming connections
    server_socket.listen()
    print('Server is listening on {}:{}'.format(*server))

    # Wait for a connection
    #print('Waiting for a connection...')
    connection, client_address = server_socket.accept()
    #print('Received connection from {}:{}'.format(*client_address))
    try:
        while True:
            # Receive the data from client
            data = connection.recv(2048)
            # Check if the video exists in the server
            request = data.decode('utf-8')
            #print('Received request: {!r}'.format(data))
            if os.path.exists(request):
                if request.endswith(".mpd"):
                    # Send the manifest file to the client
                    with open(request, 'rb') as file:
                        manifest_data = file.read()
                        #print("manifest sent")
                        connection.sendall(manifest_data)
                else:
                    # Send the video chunk to the client
                    with open(request, 'rb') as file:
                        chunk_data = file.read()
                        data_size = len(chunk_data)
                        #print("Chunk size:", data_size)
                        header = struct.pack('!I', data_size)
                        message = header + chunk_data
                        #print("Sending chunk to the client")
                        connection.sendall(message)
            else:
                # Send error message to the client
                error_message = b"video not found"
                connection.sendall(error_message)
                break
    finally:
        # Clean up the connection
        #print("Closing the connection")
        connection.close()
        server_socket.close()
                


            
if __name__ == "__main__":
    # Checking the number of arguments
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <listen_port>")
        sys.exit(1)
    elif int(sys.argv[1]) < 49152 or int(sys.argv[1]) > 65535:
        print("listen_Port number should be in the range of 49152 to 65535")
        sys.exit(1)

    listen_port = int(sys.argv[1])
    # Get the port number from the command line
    start_server(listen_port)