import socket # for UDP connection
import threading # for multi-threading
import struct # for packing and unpacking data
import select
from segmentClass import Segment


class Client:
    def init(self, src_port, dst_addr, dst_port, segment_size):
        """
        initialize the client and create the client UDP channel

        arguments:
        src_port -- the port the client is using to send segments
        dst_addr -- the address of the server/network simulator
        dst_port -- the port of the server/network simulator
        segment_size -- the maximum size of a segment (including the header)
        """
        # Create the UDP connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', src_port))
        self.timeout = 8
        self.retry = 100
        self.sock.settimeout(self.timeout)  
        self.src_port = src_port
        self.dst_addr = dst_addr
        self.dst_port = dst_port
        self.segment_size = segment_size
        self.seq_num = 0
        self.ack_num = 0
        self.num_segments = 0 
        self.base = 0
        self.next_seq_num =0
        self.packet_num = 0
        self.receive_buffer_size = 0
        self.rcv_segment_handler_thread = threading.Thread(target=self.rcv_and_sgmnt_handler)
        self.send_syn = threading.Event()
        self.connection_established = threading.Event()
        self.send_data = threading.Event()
        self.sent_data = threading.Event()
        self.closing_conn = threading.Event()
        self.rcv_segment_handler_thread.start()

        #print("The client is ready to connect")

    def rcv_and_sgmnt_handler(self):
        """
        Handles the reception of segments from the server and processes them in a separate thread.

        The method continuously checks if there are any segments ready to be received from the server. If there are, it retrieves the segment and processes it based on its flags (SYN, ACK, FIN). It also handles retransmission in case of a timeout or a corrupt segment.

        The method also checks a flag to determine if the connection is closing. If it is, it sends a FIN packet and stops receiving segments.

        If a timeout occurs while waiting for a segment, it retries a specified number of times before raising an exception. If a segment is corrupt, it also retries receiving the segment.

        Args:
            None

        Returns:
            None
        """
        
        self.rcv_data = False
        retry = self.retry
        start = True
        serverConnection = (self.dst_addr, self.dst_port)
        segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.packet_num, False, False, False)
        close = 3
        while True:
            # Waiting for main thread to send SYN packet
            if start:
                # Notify the main thread to send SYN-ACK packet
                print("SYN packet sent")
                segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.packet_num, True, False, False)
                message = segment.to_bytes(b'')
                self.sock.sendto(message, serverConnection)
                self.send_syn.set()
                
                ready_to_rcv,_,_ = select.select([self.sock], [],[], self.timeout)
                if ready_to_rcv:
                    try:
                        data, _ = self.sock.recvfrom(self.segment_size)
                        _, self.ack_num,self.packet_num, SYN, ACK, FIN, corrupt, data = segment.from_bytes(data)
                        # If segment is corrupt, retry
                        if corrupt:
                            raise ValueError("CorruptSegment")
                        start = False
                        SYN = True
                        ACK = True
                        FIN = False
                    # Preparing for retransmission
                    except (socket.timeout, ValueError) as e:
                            if retry <= 0:
                                print("Timeout occurred")
                                raise Exception(f"Failed to receive segment packet after {self.retry} attempts")  
                            elif isinstance(e, ValueError):
                                print("Received corrupt segment, retrying...")
                                start = True
                                SYN = ACK = FIN = False 
                            else:
                                print("Timeout occurred, trying again...") 
                                start = True
                                SYN = ACK = FIN = False
                            retry -= 1
            # SYN-ACK packet is received with receiver buffer size
            elif SYN == True and ACK == True and FIN == False:
                try:
                    print("SYN-ACK packet received")
                    # Extract the receive_buffer_size from data
                    receive_buffer_size_bytes = data[:4]  
                    if len(receive_buffer_size_bytes) != 4:
                        raise ValueError("receive_buffer_size_bytes must contain exactly 4 bytes of data")
                    self.receive_buffer_size = struct.unpack('!I', receive_buffer_size_bytes)[0]
                    self.seq_num += 1
                    segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.packet_num, False, True, False)
                    message = segment.to_bytes(b'')
                    self.sock.sendto(message, serverConnection)
                    print("ACK packet sent")
                    self.connection_established.set()
                    segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.packet_num, False, False, False)
                    data, addr = self.sock.recvfrom(self.segment_size)
                    _, self.ack_num,self.packet_num, SYN, ACK, FIN, corrupt, data = segment.from_bytes(data)
                    if not ( SYN or ACK or FIN) or corrupt:
                        raise ValueError("CorruptSegment")
                except (socket.timeout, ValueError) as e:
                    if retry <= 0:
                        print("Timeout occurred")
                        raise Exception(f"Failed to receive packet after {self.retry} attempts") 
                    elif isinstance(e, ValueError):
                        print("Received corrupt segment, retrying...")
                        SYN = True
                        ACK = True 
                        FIN = False
                        
                    else:
                        print("Timeout occurred, trying again...") 
                        SYN = True
                        ACK = True 
                        FIN = False
                    retry -= 1

                self.rcv_data = True
                self.send_data.set()
            # Last acknowledgment received, send FIN packet
            elif self.seq_num > 1 and self.ack_num > 1 and SYN == False and ACK == False and FIN == True:
                
                try:
                    self.seq_num += 1
                    segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.packet_num, False, False, True)
                    message = segment.to_bytes(b'')
                    self.sock.sendto(message, serverConnection)
                    print("FIN packet sent")
                    data, addr = self.sock.recvfrom(self.segment_size)
                    _, self.ack_num,self.packet_num, SYN, ACK, FIN, corrupt, data = segment.from_bytes(data)
                    if corrupt:
                        raise ValueError("CorruptSegment")
                    self.closing_conn.set()
                    break
                except (socket.timeout, ValueError) as e:
                    if close <= 0:
                        print("Server Disconnected")
                        self.closing_conn.set()
                        break
                        
                    elif isinstance(e, ValueError):
                        print("Received corrupt segment, retrying...")
                        SYN = False
                        ACK = False
                        FIN = True 
                    else:
                        print("Timeout occurred, trying again...")
                        SYN = False
                        ACK = False
                        FIN = True
                    close -= 1    

            # Sending Data
            elif self.rcv_data:
                retransmission = False
                discard = False
                expected_ack = 0
                current_buf_size = 0
                expected_length = 0
                while not self.base >= self.num_segments - 1:
                    ready_to_rcv,_,_ = select.select([self.sock], [],[], self.timeout)
                    if ready_to_rcv:
                        try:  
                            # Receive acknowledgment from server
                            data, addr = self.sock.recvfrom(self.segment_size)
                            _, self.ack_num, packet_num, SYN, ACK, FIN, corrupt, data = segment.from_bytes(data)
                            # Checks to see if rcvd the expected acknowledgement
                            if corrupt:
                                raise ValueError("CorruptSegment")
                            
                        except (socket.timeout, ValueError) as e:
                            if retry <= 0:
                                raise Exception(f"Failed to receive packet after {self.retry} attempts") 
                            elif isinstance(e, ValueError):
                                print("Received corrupt segment, retrying...")
                                ACK == False
                            else:
                                print("Timeout occurred, trying again...")
                                ACK == False
                            retry -= 1

                        if ACK == True and expected_ack == packet_num and not corrupt :
                            print("ACK for packet number:", packet_num)
                            segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.packet_num, False, False, False)
                            # Data buffer size
                            # temp1 = data[:4] 
                            # temp2 = data[4:8] 
                            # current_buf_size = struct.unpack('!I', temp1)[0]
                            # expected_length = struct.unpack('!I', temp2)[0]
                            # print(f"Current buffer size: {current_buf_size}")
                            # print(f"Expected data length: {expected_length} ")      
                            self.base += 1
                            expected_ack += 1
                            print("update base value:", self.base)
                        elif discard:
                            pass # to ignore acks
                        # update base and send the packet following the last success
                        else:
                            print(f"Packet num: {expected_ack} was not received. Discarding Incoming acknowledgments")
                            retransmission = True
                            discard = True

                    elif retransmission:
                        if expected_ack == 0 and packet_num == 0:
                            if 0 <= packet_num < self.num_segments:
                                self.base = packet_num
                            else:
                                print(f"Unexpected base value: {packet_num}. Ignoring...")
                            print("base value:", self.base)
                            self.next_seq_num = 0 # missing packet
                        else:
                            if 0 <= packet_num < self.num_segments:
                                self.base = packet_num
                            else:
                                print(f"Unexpected base value: {packet_num}. Ignoring...")
                                self.next_seq_num = 0 
                                
                            print("base value:", self.base)
                            self.next_seq_num = self.base # missing packet

                if self.base >= self.num_segments - 1:
                    # Closing socket
                    self.sent_data.set()
                    self.rcv_data = False
                    SYN = False
                    ACK = False
                    FIN = True
                   
    def connect(self):
        """
        connect to the server
        blocking until the connection is established

        it should support protection against segment loss/corruption/reordering 
        """
        # Send SYN packet
        self.send_syn.wait()
        print("SYN packet sent")

        # Wait for the connection to be established blocks until the connection is established
        self.connection_established.wait()
        print("Connection established")

    def send(self, data):
        """
        send a chunk of data of arbitrary size to the server
        blocking until all data is sent

        it should support protection against segment loss/corruption/reordering and flow control

        arguments:
        data -- the bytes to be sent to the server
        """
        
        # Split data into segments

        print("length of data:", len(data))

        segments = [data[i:i+self.segment_size - 23] for i 
                        in range(0, len(data), self.segment_size - 23)] # Split data into segments
        self.num_segments = len(segments)
        self.segments = segments
        print("Number of packets:", self.num_segments)
        windowSize = round(self.receive_buffer_size /self.segment_size)
        print("Window size:", windowSize)
        self.send_data.wait()
        print("Sending data to server...")
        self.seq_num += 1
        temp = self.base
        while not self.base >= self.num_segments and not self.sent_data.is_set() and self.base < self.num_segments :        
            while self.next_seq_num < windowSize and self.next_seq_num < self.num_segments: 
                # Create a new segment with the current sequence number and data
                segment = Segment(self.src_port, self.dst_port, self.seq_num, self.ack_num, self.next_seq_num, False, False, False)
                print("sending Packet number sent:", self.next_seq_num, "Out of:", self.num_segments - 1)
                message = segment.to_bytes(segments[self.next_seq_num])
                self.sock.sendto(message, (self.dst_addr, self.dst_port))
                self.seq_num += 1
                self.next_seq_num += 1

                if self.base > temp:
                    windowSize = windowSize + (self.base - temp)
                    temp = self.base             
            if self.sent_data.is_set() and self.base > self.num_segments - 1:
                break
            # Sliding the window
 
        print("All segments have been sent")
        return len(data)



    def close(self):
        """
        request to close the connection with the server
        blocking until the connection is closed
        """
        
        self.closing_conn.wait()
        print("Closing connection...")
        self.sock.close()