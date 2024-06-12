import socket # for UDP connection
import threading # for multi-threading
import struct # for packing and unpacking data
import queue 
import select
import time
from segmentClass import Segment

#
# Server
#
class Server:
    def init(self, src_port, receive_buffer_size):
        """
        initialize the server, create the UDP connection, and configure the receive buffer

        arguments:
        src_port -- the port the server is using to receive segments
        receive_buffer_size -- the maximum size of the receive buffer
        """
        # create the UDP connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', src_port))
        self.timeout = 8
        self.retry = 100
        self.src_port = src_port
        self.seq_num = 0
        self.ack_num = 0
        self.packet_num = 0
        self.expected_length = 0
        self.addr = None
        # configuring the receive buffer
        self.receive_buffer_size = receive_buffer_size
        self.receive_buffer = bytearray(receive_buffer_size)
        self.data_buffer = bytearray()
        self.rcv_queue = queue.Queue()

        # start the child threads
        thread1 = threading.Thread(target=self.rcv_handler)
        thread2 = threading.Thread(target=self.sgmnt_handler)
        self.syn_received = threading.Event()
        self.ack_received = threading.Event()
        self.closing_conn = threading.Event()
        self.receiving_signal = threading.Event()
        self.rcvd_signal = threading.Event()
        thread1.start()
        thread2.start()


        print("The server is ready to accept")


    def rcv_handler(self):
        """
        Handles the reception of segments from the client in a separate thread.

        The method continuously checks if there are any segments ready to be received from the client. If there are, it retrieves the segment and puts it in a queue for further processing. If a timeout occurs while waiting for a segment, it retries a specified number of times before raising an exception.

        The method also checks a flag to determine if the connection is closing. If it is, it breaks out of the loop and stops receiving segments.

        If an OSError occurs (for example, if the socket was closed), it prints a message and re-raises the exception.

        Args:
            None

        Returns:
            None
        """
        
        retry = self.retry # Number of times to retry sending segments
        while True:

            try:
                if(self.closing_conn.is_set()):
                    break
                ready_to_rcv,_,_ = select.select([self.sock], [],[], self.timeout)
                if ready_to_rcv:
                    try:
                        self.rcv_queue.put((self.sock.recvfrom(self.receive_buffer_size)))
                    except socket.timeout:
                        retry -= 1
                        if retry <= 0:
                            print("Timeout occurred in rcv_handler")
                            raise Exception(f"Failed to receive packet after {self.retry} attempts") 
                        else:
                            print("Timeout occurred in rcv_handler, trying again...")

            except OSError as e:
                if e.errno == 9:
                    print("Socket was closed")

                else:
                    raise e


    def sgmnt_handler(self):

        """
        Handles incoming segments from a client. This method is responsible for the server-side implementation of the transport protocol.

        The method continuously retrieves items from a queue of received segments. For each segment, it decodes it into its constituent parts and checks the flags to determine the type of the packet (SYN, ACK, FIN).

        If the segment is a SYN packet, the method sends a SYN-ACK back to the client. If it's an ACK packet, the method sends a message to the client indicating readiness to receive data. If it's a FIN packet, the method sends an ACK and sets a flag to indicate the closing of the connection.

        If the server is in a state to receive data (after receiving an ACK packet), it processes incoming data packets. It checks the sequence number of the packet and if it matches the expected sequence number and the packet is not corrupt, it processes the data and sends an ACK. If the sequence number doesn't match or the packet is corrupt, it discards the data and sends an ACK for the last received in-order segment.

        The method also handles timeouts and retries for buffering data.

        Args:
            None

        Returns:
            None
        """

        ts = time.time()
        timeout = False
        expected_packet = 0
        length = 0
        receive_buffer = None
        rcv = False
        SYN = ACK = FIN = False
        succ_rcv = 0
        retry = 7
        while True:
                
            queue_item = self.rcv_queue.get()
            receive_buffer = queue_item[0]
            addr = queue_item[1]
            segment = Segment(self.src_port, addr[1], self.seq_num, self.ack_num, self.packet_num, False, False, False)
            self.seq_num, _, self.packet_num, SYN, ACK, FIN, corrupt, data = segment.from_bytes(receive_buffer)

            # Check if the segment is a SYN packet
            if SYN == True and ACK == False and FIN == False:
                print("SYN packet received")
                # Send SYN-ACK
                self.ack_num += 1
                segment = Segment(self.src_port, addr[1], self.seq_num, self.ack_num, self.packet_num, True, True, False)
                message = segment.to_bytes(struct.pack('!I', self.receive_buffer_size))
                self.sock.sendto(message, addr)
                self.syn_received.set()
                print("SYN-ACK packet sent")
            # Check if the segment is an ACK packet
            elif SYN == False and ACK == True and FIN == False:
                print("ACK packet received")
                self.ack_num += 1
                segment = Segment(self.src_port, addr[1], self.seq_num, self.ack_num, self.packet_num, False, False, False)
                message = segment.to_bytes(b'ready')
                self.sock.sendto(message, addr)
                rcv = True
                self.ack_received.set()
            # Checks if the segment is a FIN packet
            elif self.seq_num > 1 and self.ack_num > 1 and SYN == False and ACK == False and FIN == True:
                print("FIN packet received")
                rcv = False
                self.rcvd_signal.set()
                self.ack_num += 1
                segment = Segment(self.src_port, addr[1], self.seq_num, self.ack_num, self.packet_num, False, True, False)
                message = segment.to_bytes(b'')
                self.sock.sendto(message, addr)
                self.closing_conn.set()
                break

            elif rcv: 
                # Handle data packet
                self.receiving_signal.wait()
                print(f"Data packet {self.packet_num}")

                if time.time() - ts > 40 and retry <= 0 :
                    print("Buffering took too long will decrease accuracy")
                    timeout = True

                if timeout: ## Account for a long time buffering to obtain a non corrupt file
                    corrupt = False
                # If the sequence number is what we expect, process the data and send an ACK
                if self.packet_num == expected_packet and not corrupt:
                    length += len(data)
                    print("packet lenght:", len(data))
                    print(f"current data_buffer length: {length}", )
                    self.data_buffer += data
                    print(f"Ack packet number {expected_packet} sent")
                    self.ack_num += 1
                    segment = Segment(self.src_port, addr[1], self.seq_num, self.ack_num, self.packet_num, False, True, False)
                    
                    # The buffer expected length to the client
                    # message = segment.to_bytes(struct.pack('!II', length, self.expected_lenght))
                    message = segment.to_bytes(b'')

                    self.sock.sendto(message, addr)
                    succ_rcv = expected_packet
                    expected_packet += 1 

                # If the sequence number is not what we expect, discard the data and send an ACK for the last received in-order segment
                else:
                    # if corrupt:
                    #     print(f"packet {self.packet_num} was corrupt. Discarding Data")

                    # else:
                    #     print(f"Out-of-order packet received. Expected packet {expected_packet}, but got {self.packet_num}. Discarding data.")
                     
                    self.ack_num += 1
                    # Send ACK for last received in-order segment
                    segment = Segment(self.src_port, addr[1], self.seq_num, self.ack_num, succ_rcv, False, True, False)
                    message = segment.to_bytes(b'')
                    self.sock.sendto(message, addr)
                    print(f"Ack packet number {succ_rcv} sent")
                    retry -= 1
                        
            receive_buffer = None

    def accept(self):
        """
        accept a client request
        blocking until a client is accepted

        it should support protection against segment loss/corruption/reordering 

        return:
        the connection to the client 
        """

        # Wait for SYN from client
        self.syn_received.wait()

        # Wait for ACK from client
        self.ack_received.wait()

        print("Connection accepted")
        # Return the connection
        conn = self.addr
        return conn

    def receive(self, conn, length):
        """
        receive data from the given client
        blocking until the requested amount of data is received
        
        it should support protection against segment loss/corruption/reordering 
        the client should never overwhelm the server given the receive buffer size

        arguments:
        conn -- the connection to the client
        length -- the number of bytes to receive

        return:
        data -- the bytes received from the client, guaranteed to be in its original order
        """
        
        self.expected_lenght = length
        self.receiving_signal.set()


        print("Receiving....")
        self.rcvd_signal.wait()
        data = self.data_buffer[:length]

        # with open('output.txt', 'w') as f:
        #     try:
        #         # Try to decode the data and write it as a string
        #         with open('output.txt', 'w') as f:
        #             f.write(data.decode())
        #     except UnicodeDecodeError:
        #         # If the data can't be decoded, write it as binary
        #         with open('output.txt', 'wb') as f:
        #             f.write(data)

        return data

    def close(self):
        """
        close the server and the client if it is still connected
        blocking until the connection is closed
        """
        self.closing_conn.wait()
        print("Closing connection...")
        self.sock.close()
