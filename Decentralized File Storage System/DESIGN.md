# A Series of Tubes

## Table of Contents

- [Project Structure](#project-structure)
- [Overview](#overview)
  - [Data Flow](#data-flow)
  - [Security Considerations](#security-considerations)
  - [Scalability](#scalability)
- [Details](#details)
  - [Blockchain Design](#blockchain-design)
    - [Block Structure](#block-structure)
    - [Chain Operations](#chain-operations)
  - [P2P Network Protocol](#p2p-network-protocol)
    - [Node Management](#node-management)
    - [Data Exchange](#data-exchange)
    - [Consensus](#consensus)
- [Decentralized File Storage System](#decentralized-file-storage-system)
  - [Application Overview](#application-overview)
  - [Functional Features](#functional-features)
  - [User Interface](#user-interface)
  - [Backend Integration](#backend-integration)
  - [Security Demonstrations](#security-demonstrations)

## Project Structure

Once `PYTHONPATH` is set to the project's root directory, its modules can be imported.

```plaintext
project-a-series-of-tubes/
│
├── DESIGN.md
├── README.md
├── TESTING.md
├── app.log
├── app/
│   ├── __init__.py
│   └── test_app.py
│
├── blocktubes/
│   ├── __init__.py
│   ├── blockchain.py
│   ├── logger.py
│   ├── peer.py
│   ├── test.sh
│   └── tracker.py
│
├── decentralized_file_storage/
│   ├── __init__.py
│   ├── app.py
│   ├── filesystem.py
│   ├── routes.py
│   ├── transaction_manager.py
│   └── templates/
│       └── index.html
│
├── pyproject.toml
├── requirements.txt
├── scripts/
│   ├── blocktubes_cli.py
│   ├── demo.py
│   ├── demo.sh
│   └── run_file_storage.sh
│
└── tests/
    ├── __init__.py
    └── test_local.py
```

## Overview

### Data Flow

- **Mining Blocks**: Users request to mine a block via the Flask app (`/mine_block`). The system calculates the proof of work and adds the new block.
- **Viewing Blockchain**: The blockchain can be viewed through the `/get_chain` endpoint, providing transparency.
- **Validation**: The `/valid` endpoint allows users to verify the integrity of the blockchain.

### Security Considerations

- **Immutable Ledger**: Utilizes cryptographic hashing to ensure that once data is written to the blockchain, it cannot be altered without consensus.
- **Consensus Algorithm**: Proof of Work provides a mechanism to achieve consensus on the blockchain state, preventing fraud.

### Scalability

- **Flask as Web Server**: Initially uses Flask’s built-in server for simplicity. For production, it is recommended to switch to a more robust server like Gunicorn.
- **Node Management**: Nodes can potentially scale by connecting to multiple peers and distributing the load.

## Details

### Blockchain Design

#### Block Structure

Each block in the blockchain contains:

- **Message**: The block message.
- **Proof**: The numerical value that miners must find to create a new block.
- **Previous Hash**: The hash of the previous block in the chain to ensure continuity.
- **Timestamp**: The UNIX timestamp when the block was created.

#### Chain Operations

- **Create Block**: Blocks are added to the chain after transactions are verified and a proof of work is found.
- **Proof of Work**: A computational challenge that miners need to solve to add a block to the chain. It helps to secure the network.
- **Chain Validation**: Ensures the integrity of the blockchain by validating each block and its position in the chain.

### P2P Network Protocol

#### Node Management

- **Node Discovery**: Nodes register themselves with a central tracker server when they join the network. The tracker assists in node discovery but does not participate in blockchain management.
- **Dynamic Peer List**: Nodes maintain an updated list of active peers through broadcasts received from the tracker, allowing for dynamic network management without central

### Data Exchange

- **Transaction Broadcasting**: Transactions are broadcast to peers to propagate the latest state of the blockchain.
- **Block Propagation**: Newly mined blocks are immediately broadcast to all peers. Each peer independently verifies each block before adding it to their blockchain.
- **Blockchain Broadcast**: The entire blockchain is broadcast to ensure all nodes are synchronized, especially useful for new nodes or after network partitions.

### Consensus

- **Achieving Consensus**: Utilizes a Proof of Work mechanism to ensure consensus on the blockchain's current state, preventing issues like double-spending and maintaining network agreement.

## Decentralized File Storage System

### Application Overview

This decentralized file storage system demonstrates how blockchain technology can be applied beyond financial transactions. It uses Flask to provide a web interface for direct user interactions with the blockchain for file operations.

### Functional Features

- **File Creation**: Users initiate file creation through a transaction, which is encapsulated in a block, uniquely identifying the file and its initial content.
- **File Append**: Users can append to existing files through transactions that reference the file and add new data in subsequent blocks.

- **File Reading**: By aggregating all transactions related to a file, from its creation to all appends, the system allows users to read a complete file.

- **File Integrity Check**: Demonstrates the blockchain's ability to maintain file integrity, ensuring that once data is added, it cannot be altered without network consensus.

### User Interface

- **Home Page**: Displays blockchain status and file listing, with options for file creation and data appending.
- **File Operations**:
  - **Create File**: Interface for specifying a file name and initial content.
  - **Append Data**: Interface for appending data to an existing file.
  - **Read File**: Functionality to read the entire content of a file, compiling all append operations recorded on the blockchain.

### Backend Integration

- **Blockchain Interaction**: The system interacts with the blockchain via API calls to manage file transactions.
- **Transaction Processing**: Manages file operations as transactions, ensuring they are validated and mined before being appended to the blockchain.

### Security Demonstrations

- **Invalid Transactions**: Demonstrates how the system rejects invalid file operations, such as appending to non-existent files.
- **Immutability Demonstrations**: Highlights how attempts to alter previously added blocks are detected and lead to disruptions in the blockchain, underscoring the security features.
