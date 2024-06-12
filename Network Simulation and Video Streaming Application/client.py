import threading
from queue import Queue
from video_player import play_chunks
import sys
import os
import socket
import time
import xml.etree.ElementTree as ET
import struct


def receive(socket, length):
    """ Receive data from the socket until the length is satisfied """
    data = b''
    while len(data) < length:
        more = socket.recv(length - len(data))
        if not more:
            raise EOFError('Was expecting %d bytes but only received %d bytes before the socket closed' % (length, len(data)))
        data += more
    return data

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    """
    the client function
    write your code here

    arguments:
    server_addr -- the address of the server
    server_port -- the port number of the server
    video_name -- the name of the video
    alpha -- the alpha value for exponentially-weighted moving average
    chunks_queue -- the queue for passing the path of the chunks to the video player
    """
    
    #print("Client started")

    # Establish a TCP connection to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    network = (server_addr,server_port)
    client_socket.connect(network)
    start_time = time.time()

    # Request the manifest file from the server
    #print("Requesting the manifest file from the server")
    request = "./data/"+ video_name + "/manifest.mpd"
    client_socket.sendall(request.encode("utf-8"))

    # Receive the manifest file from the server
    manifest_data = client_socket.recv(2048)
    if manifest_data == b"video not found":
        print("video not found")
        client_socket.close()
        return
    else:
        #print("manifest file received")
        manifest_data = ET.fromstring(manifest_data.decode("utf-8"))

    # Parse the manifest file
    bitrates = [int(representation.get('bandwidth')) for representation in manifest_data.findall('.//Representation')]
    num_chunks = int(float(manifest_data.get('mediaPresentationDuration')) / float(manifest_data.get('maxSegmentDuration')))
    
    #print("Number of Chunks:", num_chunks)
    bitrates.sort()
    #print("List of Bitrates:", bitrates)

    chunk_names = []
    for bitrate in bitrates:
        bitrate_chunks = []
        for chunk_number in range(num_chunks):
            chunk_number_str = str(chunk_number).zfill(5)  # Represent chunk number with 5 digits
            chunk_name = f"{video_name}_{bitrate}_{chunk_number_str}.m4s"
            bitrate_chunks.append(chunk_name)
        chunk_names.append(bitrate_chunks)

    # print("List of Chunk Names:", chunk_names)
  
    # Initialize the throughput and throughput estimation by choosing the minimum bitrate
    i = 0
    log_file = open("log.txt", "w")
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    T_current = min(bitrates)
    buff_size = 2000000000
    
    # Request the video chunks from the server
    for p in range(num_chunks):
        ts = time.time()
        current_chunk = chunk_names[i][p]
        chunk_path = "./data/" + video_name + "/chunks/" + current_chunk
        #print ("Requesting chunk: ", current_chunk)
        client_socket.sendall(chunk_path.encode("utf-8"))

        header_length = 4 # 4 bytes for the header
        header = client_socket.recv(header_length)
        data_length = struct.unpack('!I', header)[0]
        chunk_data = receive(client_socket, data_length)

        #print("Chunk received:", current_chunk)
        tf = time.time()

        with open("tmp/" + current_chunk, 'wb') as file:
            file.write(chunk_data)

        chunk_rcvd_path = "tmp/" + current_chunk

        # Calculate the network Throughput
        chunk_size = len(chunk_data) * 8
        download_time = tf - ts
        T_new = chunk_size / download_time

        # Using ABR algorithm to update the throughput
        T_current =  alpha * T_new + (1 - alpha) * T_current

        # Determine the next bitrate
        T_avg =  T_current
        if T_avg < 1.5 * min(bitrates):
            # if the throughput is less than 1.5 times the lowest bitrate, choose the lowest bitrate
            next_bitrate = min(bitrates)
        else:
            # if the throughput is greater than 1.5 times the lowest bitrate, choose the highest bitrate that is less than or equal to 1.5 times the throughput
            next_bitrate = max(bitrate for bitrate in bitrates if bitrate <= T_avg / 1.5)

        i = bitrates.index(next_bitrate)
        chunks_queue.put(chunk_rcvd_path)
        end_time = time.time()
        log_file.write(str(end_time - start_time) + " " + str(download_time) + " " + str(T_new) + " " + str(T_current) + " " + str(next_bitrate) + " " + str(current_chunk) + "\n")
       
    client_socket.close()
    log_file.close()
    



    # Note: the duration should increase by max segment duration go to office hours to fix this

# parse input arguments and pass to the client function
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <network_addr> <network_port> <name> <alpha>")
        sys.exit(1)

    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    video_name = sys.argv[3]
    alpha = float(sys.argv[4])

    # init queue for passing the path of the chunks to the video player
    chunks_queue = Queue()
    # start the client thread with the input arguments
    client_thread = threading.Thread(target = client, args =(server_addr, server_port, video_name, alpha, chunks_queue))
    client_thread.start()
    # start the video player
    #play_chunks(chunks_queue)
