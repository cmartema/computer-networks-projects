import time # for sleep & log files
import struct # for packing and unpacking data
import hashlib # To convert checksum

class Segment:
    def __init__(self, src_port, dst_port, seq_num=0, ack_num=0, packet_num=0, syn=False, ack=False, fin=False):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.syn = syn
        self.ack = ack
        self.fin = fin
        self.packet_num = packet_num
        

    def to_bytes(self, data):
        """
        Constructs a segment and returns it as bytes.

        The method first converts the SYN, ACK, and FIN flags to a single byte. It then packs the sequence number, acknowledgment number, packet number, and flags into a byte array to form the header.

        The payload is formed by concatenating the header and the data. A checksum is then calculated for the payload.

        The method returns the checksum, header, and data concatenated together.

        Args:
            data (bytes): The data to be included in the segment.

        Returns:
            bytes: The constructed segment as bytes.
        """

        # Convert flags to a single byte
        flags = (self.syn << 2) | (self.ack << 1) | self.fin
        # Pack header fields and data into a byte array
        self.log(data)   # Log the segment information
        header = struct.pack('!HHHB', self.seq_num, self.ack_num, self.packet_num, flags)
        payload = header + data
        checksum = self.checksum(payload)
        return checksum + header + data #  16 + 7 + len(data)
    
    
    def from_bytes(self, segment):
        """
        Extracts segment information from the given bytes.

        The method first unpacks the checksum from the first 16 bytes of the segment. It then unpacks the header fields from the next 7 bytes of the segment and assigns them to the corresponding instance variables.

        The flags are then extracted from the header and used to set the SYN, ACK, and FIN flags.

        The data is extracted from the remaining bytes of the segment. If the data is None or all bytes are 0, the segment is not considered corrupt. Otherwise, the method checks if the data is corrupt by comparing the checksum of the segment (excluding the checksum) with the extracted checksum.

        The method logs the segment information and returns a tuple containing the sequence number, acknowledgment number, packet number, SYN flag, ACK flag, FIN flag, corruption status, and data.

        Args:
            segment (bytes): The segment from which to extract information.

        Returns:
            tuple: A tuple containing the sequence number, acknowledgment number, packet number, SYN flag, ACK flag, FIN flag, corruption status, and data.
        """

        # Unpack the header fields and data from the byte array
        checksum = segment[:16]
        header = struct.unpack('!HHHB', segment[16:23])
        self.seq_num = header[0]
        self.ack_num = header[1]
        self.packet_num = header[2]
        flags = header[3]
        self.syn = bool(flags & 0b100)
        self.ack = bool(flags & 0b010)
        self.fin = bool(flags & 0b001)
        data = segment[23:]

        if data is None and all(b == 0 for b in data):
            corrupt = False
        else:
            corrupt = self.is_data_corrupt(segment[16:], checksum)

        self.log(data)   # Log the segment information
        return (self.seq_num, self.ack_num, self.packet_num, self.syn, self.ack, self.fin, corrupt, data)
    
    def is_data_corrupt(self, data, checksum):
        """
        This function checks if the data is corrupted by comparing the calculated checksum of the data with a provided checksum.

        Parameters:
        data -- The data that you want to check for corruption. It could be any data type that is accepted by the checksum function, but it's typically a string or bytes.
        checksum -- A function that calculates the checksum of the data. It takes the data as input and returns a checksum. The checksum is a value that is used to check the integrity of the data. If the data is changed in any way, the checksum will also change.

        Returns:
        True if the calculated checksum of the data does not match the provided checksum (indicating the data is corrupted), False otherwise.
        """
        return self.checksum(data) != checksum 


    def checksum(self, data):
        return hashlib.md5(data).digest()

    def log(self, data):
        """
        Logs the segment information.

        The method first determines the type of the segment based on the SYN, ACK, and FIN flags, the packet number, the acknowledgment number, and the sequence number. The type of the segment is then used to set the segment_type variable.

        The method then opens a log file named 'log_{self.src_port}.txt' in append mode and writes the current time, source port, destination port, sequence number, acknowledgment number, segment type, and length of the data to the file.

        Args:
            data (bytes): The data of the segment.

        Returns:
            None
        """
        # Default value for segment_type
        segment_type = 'UNKNOWN'

        # Determine the type of the segment
        if self.syn and self.ack:
            segment_type = 'SYN-ACK'
        elif self.syn:
            segment_type = 'SYN'
        elif data[:5] == 'ready' and not (self.syn and self.ack and self.fin):
            segment_type = 'ACK'
        elif self.ack:
            if self.packet_num >= 0 and (self.ack_num > 1 or self.seq_num > 1) :
                segment_type = f'ack{self.packet_num}'
            else: 
                segment_type = 'ACK'
        elif self.fin:
            segment_type = 'FIN' 
        else:
            if self.seq_num > 0 and self.ack_num > 0:
                segment_type = f'pkt{self.packet_num}'
                

        # Log the segment information
        with open(f'log_{self.src_port}.txt', 'a') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} {self.src_port} {self.dst_port} {self.seq_num} {self.ack_num} {segment_type} {len(data)}\n')