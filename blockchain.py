import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block (the starting block)
        self.new_block(previous_hash=1, proof=100)
    
    def register_node(self, address):
        """
        Add a new node to list of nodes
        Parameters:
        - address: <str> Address of node
        Return:
        - None
        """
        
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self, chain):
        """Determine if a blockchain is valid
        Parameters:
        - chain: <list> A blockchain
        Return:
        - <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n---------\n")
            
            # Check the hash of block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # Check that proof of work is valid
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        return True
    
    def resolve_conflicts(self):
        """Consensus algorithm replaces the chain with the longest one in the network.
        Return:
        - <bool> True if chain was replaced, False if not
        """

        neighbors = self.nodes
        new_chain = None

        # Look for longer chains
        max_length = len(self.chain)

        # Find and verify chains from all nodes in the network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True
        return False
    
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
    
# Instantiate the node
app = Flask(__name__)

# Make a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def min():
    # Run proof of work algorithm to get next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Receive reward for finding proof
    # Sender is 0 to show the node mined a new coin
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    # Forge new block by adding to chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New block forged", 
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    } 
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check the required fields are in the POST data
    required = ['sender', 'recipient', 'amount']
    if not all(value in values for value in required):
        return 'Missing values', 400
    
    # Create new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return "Error: invalid list of nodes"

    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': "New nodes have been added",
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': "Chain has been replaced",
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': "Chain was not replaced",
            'chain': blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)