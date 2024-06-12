# CSEE 4119 Spring 2024, Assignment 2 Design File
## Cristopher Marte Marte (cjm2301)
## GitHub username: cmartema


## Protocol Design

### Message Types

1. **SYN**: Synchronization message used to establish a connection. It's identified by the `syn` flag being `True` and the `ack` flag being `False`.

2. **ACK**: Acknowledgment message used to acknowledge the receipt of a packet. It's identified by the `ack` flag being `True`.

3. **SYN-ACK**: Synchronization and acknowledgment message used in the three-way handshake process of establishing a connection. It's identified by both the `syn` and `ack` flags being `True`.

4. **FIN**: Finish message used to close a connection. It's identified by the `fin` flag being `True`.

5. **Data Packet**: A packet containing data. It's identified by the `seq_num` and `ack_num` being greater than `0` and all flags (`syn`, `ack`, `fin`) being `False`.

### Protocol Elements

1. **Sequence Number (`seq_num`)**: Used for ordering packets and ensuring data is delivered without duplication.

2. **Acknowledgment Number (`ack_num`)**: Used to acknowledge the receipt of packets.

3. **Packet Number (`packet_num`)**: Used to identify packets.

4. **Checksum**: Used to check the integrity of the data. It's calculated using the MD5 hash of the data.

5. **Flags**: Used to identify the type of the message. There are three flags: `syn`, `ack`, and `fin`.

### Reliable Data Transfer

Reliable data transfer is achieved through the use of sequence numbers, acknowledgment numbers, and checksums. Sequence numbers ensure data is delivered in order and without duplication. Acknowledgment numbers are used to acknowledge the receipt of packets. Checksums are used to check the integrity of the data and detect any corruption that might have occurred during transmission. The protocol also uses the Go-Back-N (GBN) algorithm for reliable data transfer. In GBN, the sender can send several segments without waiting for acknowledgments, but if a segment is lost or corrupted, all segments sent after the lost one are retransmitted. This ensures that the receiver receives all segments in the correct order.

### Logging

The `log` method is used to log the segment information, including the source port, destination port, sequence number, acknowledgment number, segment type, and data length. The log is written to a file named `log_{self.src_port}.txt`.

### Segment Construction and Extraction
The `to_bytes` method is used to construct a segment and return it as bytes. The `from_bytes` method is used to extract segment information from the given bytes.

#### Segment Construction: `to_bytes`
The `to_bytes` method is used to construct a segment from the given data and return it as bytes. Here's a step-by-step breakdown of how it works:
  1. The method takes a data argument, which is the data to be included in the segment.
  2. The SYN, ACK, and FIN flags are converted to a single byte.
  3. The sequence number, acknowledgment number, packet number, and flags are packed into a byte array to form the header using the `struct.pack` function.
  4. The payload is formed by concatenating the header and the data.
  5. A checksum is calculated for the payload.

6. The method returns the checksum, header, and data concatenated together.

#### Segment Extraction: `from_bytes`
The `from_bytes` method is used to extract segment information from the given bytes. Here's a step-by-step breakdown of how it works:
  1. The method takes a byte array (segment) as an argument, which represents the segment from which information is to be extracted.
  2. The checksum is extracted from the first 16 bytes of the segment.
  3. The header fields are unpacked from the next 7 bytes of the segment using the `struct.unpack` function. This unpacks the sequence number, acknowledgment number, packet number, and flags from the byte array and assigns them to the corresponding instance variables.
  4. The flags are then processed to set the SYN, ACK, and FIN flags of the Segment object.

5. The data is extracted from the remaining bytes of the segment.

6. The method then checks if the data is corrupt. If the data is None or all bytes are 0, the segment is not considered corrupt. Otherwise, the `is_data_corrupt` method is called to check if the data is corrupt.

7. The method logs the segment information and returns a tuple containing the sequence number, acknowledgment number, packet number, SYN flag, ACK flag, FIN flag, corruption status, and data.
