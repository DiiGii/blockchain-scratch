# blockchain-scratch
A simple blockchain implemented from scratch in Python (using Flask, requests library, and Postman). 

## What is a blockchain? 

A **blockchain** is an immutable, sequential chain of records that are called blocks. These blocks are chained together using **hashes**. 
In this simplified design, each block contains:
- An index
- A timestamp (Unix time)
- A list of transactions
- A proof
- A hash of the previous block

Because each block contains a hash of the previous block, we have created a chain of dependencies. So if an attacker attempts to change the data within a particular block, the hash of that block would change. This leads to a cascading effect where all later blocks will become invalid. This concept of chaining is fundamental to a blockchain's immutability. 

## Transactions
In blockchain, **transactions** are a record of an event or action. For instance, a transfer of cryptocurrency from one party to another. Transactions are added to each block, and return the index of the next block to be mined. **Mining** is the process where: 
1. Pending transactions are gathered into blocks
2. Transactions are validated
3. A proof-of-work is created (more on that later)
4. The new block is added to the chain, making the transaction inside it permanent and secure

So in our `new_transaction` method, along with later code, we are essentially following this process: 
1. The transaction is now in a queue of pending transactions waiting to be included in the next block that a miner successfully creates.
2. Miners on the network will compete to solve the computational problem for this next block.
3. Once a miner solves the problem, that block (containing your transaction) will be added to the blockchain.

## Proof of work
Proof-of-work (PoW) is a way to confirm transactions and add new blocks to a blockchain by requiring computers to solve complex math problems. It's like a computational puzzle that's hard to solve but easy to verify.

As an analogy:
- Imagine a group of people trying to solve a giant Sudoku puzzle. The first person to solve it gets to write the next page in a public notebook (the blockchain). Everyone can easily check if the solution (proof) is correct, but it takes a lot of effort to find the solution in the first place.

In our implementation, we simply check if the hash of the last proof and the current proof contains 4 leading zeroes. 

Finally, a Flask server is used to setup "nodes" in our blockchain network. Mining endpoints are then defined to:
- Perform the proof-of-work computation.
- Credit ourselves (as the miner) with a reward of 1 coin via a new transaction.
- Append the newly created block to the existing blockchain.

## Consensus
This is great! We've built a basic blockchain that handles transactions and mining. However, a key aspect of blockchains is decentralization. This raises the question: how do we ensure all copies of the blockchain are identical when it's distributed? This is the consensus problem, and we'll need a **consensus algorithm** to support multiple nodes in our network.

In our consensus algorithm, we define a consensus by the maximum length of the chain. That is, if a valid chain is found in neighboring nodes, whose length is greater than ours, we replace our chain.



