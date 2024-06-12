import argparse
import dataclasses
import json
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Dict, List

from blocktubes.logger import block_logger
from blocktubes.peer import Peer

@dataclass
class File:
    name: str
    content: str


@dataclass
class BlockFileSystem:
    # Filenames are double encoded for ease of access
    # A filesystem can be constructed from FileTransactions encoded on a blockchain
    files: Dict[str, File] = field(default_factory=dict)


class FileAction(IntEnum):
    UNKNOWN = 0  # Leave the first value unset to catch errors
    CREATE = auto()
    APPEND = auto()
    DELETE = auto()


@dataclass
class FileTransaction:
    action: FileAction
    filename: str
    file_content: str = ""


class BlockFileSystemPeer(Peer):
    def __init__(self, port: int, tracker_host: str, tracker_port: int):
        super().__init__(port, tracker_host, tracker_port)
        self.file_system_cache = BlockFileSystem()
        
    def list_files(self) -> List[str]:
        file_system = self.construct_filesystem()
        return [filename for filename in file_system.files.keys()]

    def create_file(self, filename: str):
        file_system = self.construct_filesystem()
        if filename in file_system.files:
            block_logger.error(f"Attempt to create a file that already exists: {filename}. Operation rejected.")
            raise KeyError(f"File already exists: {filename}")
        
        create_transaction = FileTransaction(action=FileAction.CREATE, filename=filename)
        return self.broadcast_transaction(create_transaction)

    def append_file(self, filename: str, content: str):
        file_system = self.construct_filesystem()
        if filename not in file_system.files:
            block_logger.error(f"Attempt to append to a non-existent file: {filename}. Operation rejected.")
            raise KeyError(f"File not found: {filename}")
        
        append_transaction = FileTransaction(action=FileAction.APPEND, filename=filename, file_content=content)
        response = self.broadcast_transaction(append_transaction)
        return response
    
    def delete_file(self, filename: str):
        file_system = self.construct_filesystem()
        if filename not in file_system.files:
            block_logger.error(f"Attempt to delete a non-existent file: {filename}. Operation rejected.")
            raise KeyError(f"File not found: {filename}")
        
        delete_transaction = FileTransaction(action=FileAction.DELETE, filename=filename)
        response = self.broadcast_transaction(delete_transaction)
        
        # Immediately delete the file from the file_system
        del file_system.files[filename]
        
        return response

    def read_file(self, filename: str) -> str:
        file_system = self.construct_filesystem()
        if filename not in file_system.files:
            raise KeyError(f"Unable to find {filename=} in filesystem")
        return file_system.files[filename].content
    
    def simulate_tampering(self, filename, new_content):
        for block in self.blockchain.chain:
            if not block.message.strip():  # Check if the message is not empty and not just whitespace
                block_logger.info("Skipping block with empty message")
                continue
            
            try:
                transaction = json.loads(block.message)
            except json.JSONDecodeError as e:
                block_logger.error(f"JSON decoding failed for block message: {block.message} with error {e}")
                continue  # Skip this block and move to the next

            if transaction.get('filename') == filename:
                original_message = block.message
                transaction['file_content'] = new_content
                block.message = json.dumps(transaction)
                
                if not self.blockchain.is_valid_chain(self.blockchain.chain):
                    block.message = original_message  # Revert to original if tampering detected
                    return "Tampering detected and reverted. Blockchain integrity maintained."
                block.message = original_message
                return "Tampering not detected. Blockchain integrity is compromised."

        return "File not found in the blockchain."


    def broadcast_transaction(self, transaction: FileTransaction):
        encoded_transaction = json.dumps(dataclasses.asdict(transaction))
        return self.mine_and_broadcast_block(encoded_transaction)

    def construct_filesystem(self) -> BlockFileSystem:
        file_system = BlockFileSystem()

        for block in self.blockchain.chain[1:]:  # Skip the genesis block
            try:
                transaction = FileTransaction(**json.loads(block.message))
            except json.JSONDecodeError as e:
                block_logger.error(f"Failed to decode transaction from block {block.block_index}: {e}")
                continue

            filename = transaction.filename
            if transaction.action == FileAction.CREATE:
                if filename in file_system.files:
                    block_logger.error(f"Duplicate create transaction ignored for {filename}.")
                    continue
                file_system.files[filename] = File(name=filename, content="")
                block_logger.info(f"File created: {filename}")
            elif transaction.action == FileAction.APPEND:
                if filename not in file_system.files:
                    block_logger.error(f"Attempt to append to non-existent file {filename} ignored.")
                    continue
                file_system.files[filename].content += transaction.file_content
                block_logger.info(f"Content appended to {filename}.")
            elif transaction.action == FileAction.DELETE:
                if filename in file_system.files:
                    del file_system.files[filename]
                    block_logger.info(f"File deleted: {filename}")
                else:
                    block_logger.error(f"Attempt to delete non-existent file {filename} ignored.")

        self.file_system_cache = file_system
        return file_system


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a peer connection to tracker.")
    parser.add_argument("port", type=int, help="Port number for this peer")
    parser.add_argument("--tracker_host", help="Hostname of the tracker", default="localhost")
    parser.add_argument("--tracker_port", type=int, help="Port number of the tracker", default=50_000)
    args = parser.parse_args()
    peer = BlockFileSystemPeer(args.port, args.tracker_host, args.tracker_port)
    peer.start()