import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import flask

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block (the starting block)
        self.new_block(previous_hash=1, proof=100)
    
    def new_block(self, proof, previous_hash=None):
        """
        Create a block and add to chain
        Parameters:
        - proof: <int> The proof given by proof of work algorithm
        - previous_hash (Optional): <str> Hash of previous block
        Return:
        - <dict> New block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset current list of transactions
        self.current_transactions = []
        self.chain.append(block)

        return block
        

    def new_transaction(self, sender, recipient, amount):
        """
        Add new transaction to list of transactions
        Parameters:
        - sender: <str> Address of sender
        - recipient: <str> Address of recipient
        - amount: <int> Amount
        Return:
        - <int> the index of the block that holds this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        # Hashes a block
        """Create a SHA-256 hash of a block
        Parameters:
        - block: <dict> Block
        Return:
        - <str> Hash of block
        """

        # Order dictionary for consistent hashing
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last block in the chain
        return self.chain[-1]
    
    def proof_of_work(self, last_proof):
        """
        Simplified proof of work algorithm:
        - Find a number q such that hash(pq) contains 4 leading zeroes
        - Where p is previous proof and q is new proof
        Parameters:
        - last_proof: <int>
        Return:
        - <int> 
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof: Does hash(last_proof, proof) contain 4 leading zeroes
        Parameters:
        - last_proof: <int> Previous proof
        - proof: <int> Current proof
        Return:
        - <bool> True if valid, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"