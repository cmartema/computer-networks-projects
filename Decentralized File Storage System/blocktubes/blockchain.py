import dataclasses
import json
import logging
import time
from dataclasses import dataclass, field
from hashlib import sha256
from typing import List, Optional

blockchain_logger = logging.getLogger("blockchain_logger")


@dataclass
class Block:
    prev_hash: str
    proof: str
    block_index: int
    message: str = ""
    unix_timestamp: float = field(default_factory=lambda: time.time())


def hash_block(block: Block):
    return sha256((block.prev_hash + block.message + block.proof).encode()).hexdigest()


def validate_hash(hash: str, difficulty: int) -> bool:
    return hash.startswith("0" * difficulty)


def encode_block(block: Block) -> str:
    return json.dumps(dataclasses.asdict(block))


class BlockChain:
    def __init__(self, hash_difficulty: int):
        self.hash_difficulty = hash_difficulty
        self.chain: List[Block] = []
        self.chain.append(Block(prev_hash="", proof="arbitrary_val", block_index=0))

    def proof_of_work(self, message: str, max_attempts: int = 10_000) -> Optional[Block]:
        # Set a max attempts to prevent an infinite loop
        prev_block = self.chain[-1]
        prev_hash = hash_block(prev_block)
        block_index = len(self.chain)
        for i in range(max_attempts):
            candidate_block = Block(prev_hash=prev_hash, block_index=block_index, message=message, proof=str(i))
            if validate_hash(hash_block(candidate_block), difficulty=self.hash_difficulty):
                return candidate_block
        return None

    def is_valid_chain(self, chain):
        prev_hash = hash_block(chain[0])
        for block_index, block in enumerate(chain[1:]):
            if block.prev_hash != prev_hash:
                return False
            if block.block_index != block_index + 1:
                return False
            if not validate_hash(hash_block(block), self.hash_difficulty):
                return False
            prev_hash = hash_block(block)
        return True

    def assert_valid_chain(self):
        # Skip the first block because the values are arbitrary
        prev_hash = hash_block(self.chain[0])
        for i, block in enumerate(self.chain[1:]):
            assert block.prev_hash == prev_hash
            block_hash = hash_block(block)

            logging.info(f"Validate block {i}, {block_hash=}")
            assert validate_hash(block_hash, self.hash_difficulty)
            prev_hash = block_hash

    def mine_block(self, message: str) -> Optional[Block]:
        block = self.proof_of_work(message)
        if block:
            self.chain.append(block)
            return block
        return None

    def validate_and_add_block(self, block: Block) -> bool:
        """Validates a block and adds it to the blockchain if valid.

        Args:
            block (Block): The block to validate and add.

        Returns:
            bool: True if the block was added, False otherwise.
        """
        # Check if the blockchain is empty or the block is the next in the chain
        if self.chain and block.prev_hash != hash_block(self.chain[-1]):
            logging.warning("Block has incorrect previous hash.")
            return False

        # Validate the proof of work
        block_hash = hash_block(block)
        if not validate_hash(block_hash, self.hash_difficulty):
            logging.warning("Block fails proof of work validation.")
            return False

        if block.unix_timestamp < self.chain[-1].unix_timestamp:
            logging.warning("Block was created with an older timestamp.")
            return False

        # Append the block to the chain
        self.chain.append(block)
        logging.info(f"Block added to blockchain: {block_hash}")
        return True

    def get_block_messages(self) -> List[str]:
        block_messages = [block.message for block in self.chain[1:]]
        return block_messages


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    blockchain = BlockChain(hash_difficulty=3)
    logging.info(blockchain.mine_block("first block"))
    logging.info(blockchain.mine_block("second block"))
    logging.info(blockchain.mine_block("third block"))

    blockchain.assert_valid_chain()
