# Workspace Overview

This workspace contains several projects, each with its own unique structure and purpose. Below is a brief overview of each project and its hierarchy.

## Decentralized File Storage System

This project is a decentralized file storage implemented as a peer-to-peer blockchain network. The blockchain implementation provides high availability of data and automatic validation of data integrity without relying on a single authority. Additionally, it provides a graphical web interface for interacting with the filesystem.

- `.gitignore`: Specifies intentionally untracked files to ignore.
- `blocktubes/`: Contains the blockchain implementation.
- `decentralized_file_storage/`: Contains the file storage system.
- `DESIGN.md`: Describes the design of the system.
- `img/`: Contains images used in documentation.
- `pyproject.toml`: Specifies the build system requirements and project metadata.
- `README.md`: Provides an overview of the project.
- `requirements.txt`: Lists the Python dependencies required by the project.
- `scripts/`: Contains scripts used in the project.
- `TESTING.md`: Describes the set of tests run to demonstrate the resilience of the blockchain.
- `tests/`: Contains the test suite for the project.

## Distance Vector Routing (DVR) Program

This project implements a Distance Vector Routing (DVR) program.

- `dvr.py`: Contains the main implementation of the DVR program.
- `launch.py`: Script to launch the program.
- `overlay`: Contains the network overlay for the DVR program.
- `README.md`: Provides an overview of the project.
- `TESTING.md`: Describes the testing procedures for the DVR program.

## Mini Reliable Transport Protocol

This project implements a Mini Reliable Transport Protocol.

- `app_client.py`: Contains the client-side application code.
- `app_server.py`: Contains the server-side application code.
- `data.txt`: Contains data used in the project.
- `DESIGN.md`: Describes the design of the transport protocol.
- `loss.txt`: Contains information about packet loss in the network.
- `mrt_client.py`: Contains the client-side MRT code.
- `mrt_server.py`: Contains the server-side MRT code.
- `network.py`: Contains the network implementation.
- `README.md`: Provides an overview of the project.

## Network Simulation and Video Streaming Application

This project simulates a network and implements a video streaming application. The network simulation is designed to mimic real-world network conditions, including latency, jitter, and packet loss. The video streaming application uses adaptive bitrate streaming to optimize video quality based on network conditions.

- `bw.txt`: Contains bandwidth data for the network simulation.
- `network_simulator.py`: Contains the main implementation of the network simulator.
- `video_streaming.py`: Contains the implementation of the video streaming application.
- `adaptive_bitrate.py`: Contains the implementation of the adaptive bitrate algorithm.
- `latency.txt`: Contains data about network latency for the simulation.
- `jitter.txt`: Contains data about network jitter for the simulation.
- `packet_loss.txt`: Contains data about packet loss in the network.
- `video_files/`: Directory containing video files for streaming.
- `README.md`: Provides an overview of the project.
- `TESTING.md`: Describes the testing procedures for the network simulation and video streaming application.