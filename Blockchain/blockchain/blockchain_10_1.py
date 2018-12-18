'''
title           : blockchain.py
description     : A blockchain implemenation
author          : Adil Moujahid
date_created    : 20180212
date_modified   : 20180309
version         : 0.5
usage           : python blockchain.py
                  python blockchain.py -p 5000
                  python blockchain.py --port 5000
python_version  : 3.6.1
Comments        : The blockchain implementation is mostly based on [1]. 
                  I made a few modifications to the original code in order to add RSA encryption to the transactions 
                  based on [2], changed the proof of work algorithm, and added some Flask routes to interact with the 
                  blockchain from the dashboards
References      : [1] https://github.com/dvf/blockchain/blob/master/blockchain.py
                  [2] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
'''

from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS



#MINING_SENDER = "THE BLOCKCHAIN"
MINING_SENDER = "The same"
MINING_REWARD = 1
#MINING_DIFFICULTY = 2
MINING_DIFFICULTY = 4
#IP_self='127.0.0.1'
#port_self=5000
IP_self='127.0.0.1'
port_self=2000
#transactions_empty=0

class Blockchain:
    #transactions_empty=0
    def __init__(self):
        
        self.transactions = []
        self.chain = []
        self.nodes = set()
        #Generate random number to be used as node_id
        self.node_id = str(uuid4()).replace('-', '')
        #Create genesis block
        #self.create_block(0, '00')
        #self.create_block(0)
        self.create_block()


    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        #Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def verify_transaction_signature(self, value_public_key_to_master, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        #public_key = RSA.importKey(binascii.unhexlify(sender_address))
        public_key = RSA.importKey(binascii.unhexlify(value_public_key_to_master))
        #public_key = value_public_key_to_master
        print('\n\n @@@@@ verify_transaction_signature :::  public_key  = ', public_key)
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))


    def submit_transaction(self, sender_address, recipient_address, value_voltage, value_current,     value_power,value_energy,value_datatime,value_transaction_energy,value_public_key_to_master,signature):
        """
        Add a transaction to transactions array if the signature verified
        """
        transaction = OrderedDict({'sender_address': sender_address, 
                                    'recipient_address': recipient_address,
                                    'value_voltage': value_voltage,
                                    'value_current': value_current,
                                    'value_power': value_power,
                                    'value_energy':value_energy,
                                    'value_datatime':value_datatime,                                   
                                    'value_transaction_energy':value_transaction_energy,
                                    'value_public_key_to_master': value_public_key_to_master})   

        print('\n\n @@@@ transaction = ')
        print('\n\n transaction = ',transaction)
        #Reward for mining a block
        #if asender_address == MINING_SENDER:
        if value_public_key_to_master == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        #Manages transactions from wallet to another wallet
        else:
            #transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
            transaction_verification = self.verify_transaction_signature(value_public_key_to_master , signature, transaction)
            print('\n\n transaction_verification ::: ')
            print('\n\n transaction_verification = ',transaction_verification)
            #print('\n\n $$$$$ signature = ',signature)
            
            if transaction_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False


    #def create_block(self, nonce,   previous_hash):
    #def create_block(self, nonce):
    def create_block(self):
        """
        Add a block of transactions to the blockchain
        """
        """
        block = {'block_number': len(self.chain) + 1,
                'timestamp': time(),
                'transactions': self.transactions,
                'nonce': nonce,
                'previous_hash': previous_hash}

        # Reset the current list of transactions
        self.transactions = []

        self.chain.append(block)
       
        """
        global previous_hash
        print('\n\n     ####       self.transactions= ',self.transactions)
        if (self.transactions==[]):
            print('\n\n !!!  else: !!!  ')
            #block_now=
            # hash=hash(self, block)
            previous_hash=0
            #previous_has="8fb156e516b52afffb5860b5e3a076b0513c0d2d4489a9c4675c98e7e4a48a0d"
            #current_hash = hash(str(previous_hash) )
            nonce=0
            current_hash = "8fb156e516b52afffb5860b5e3a076b0513c0d2d4489a9c4675c98e7e4a48a0d"
            ##current_hash_a = proof_of_work()
            #current_hash = current_hash_a[0]
            block = {'block_number': len(self.chain) + 1,
                     'timestamp': time(),
                     'transactions':'999',
                     'nonce': nonce,
                     'previous_hash':previous_hash,
                     'hash':current_hash}
            #self.transactions = []
            previous_hash=current_hash
            
            if len(self.chain)==0 :
                transactions_empty=1
                print('\n\n !!! if len(self.chain)==0 :  transactions_empty=',transactions_empty)
                self.chain.append(block)
                print('self.chain.remove(block)==',block)
                print('len(self.chain)==',len(self.chain))
                #print('transactions_empty===',transactions_empty)
            return block

        else: 
            print('\n\n ####       if (self.transactions!=[]):= ')
            #transactions_empty=0
            #temp=transactions_empty
            chain_0= self.chain[0]
            print('\n\n !!! chain_0;;;',chain_0)
            print('\n\n !!! type chain_0',type(chain_0))
            #print('\n\n ####       self.chain[0][2]= ',self.chain[0][2])
            #if (len(self.chain)== 1 and  temp== 1):
            #print('n\n !!! iself.chain[0] :',self.chain[0])
            #print('n\n !!! iself.chain[0] :',value(self.chain[0].['transactions']))
            #if (len(self.chain)== 1 and  self.chain[0].['transactions']== '999'):
            #if (len(self.chain)== 1 and chain_0['transactions']=='999'):   
                #transactions_empty=transactions_empty+1
            #    print('\n\n !!! if (len(self.chain)== 1 and  transactions_empty== 0):')
             ##   print('\n\n !!! type self.chain',type(self.chain))
              #  print('c !!! type self.chain[0]',type(self.chain[0]))
                # chain_0= self.chain[0]
                ##print('\n\n !!! type chain_0',type(chain_0))
                #self.chain.remove(self.chain[0])
                
                #self.chain.remove(self.chain[0])
                #if len(self.chain)==0 : 
            current_hash= self.proof_of_work()
            #previous_hash=hash(str(0) )
            #current_hash = hash(str(previous_hash)+str(nonce)+str(self.transactions))
            current_hash_a= self.proof_of_work()
            #current_hash_a = proof_of_work()
            nonce = current_hash_a[0]
            current_hash = current_hash_a[1]
            
            print('\n\n@@@@  After self.chain.remove(block)==',self.chain)
            print('len(self.chain)==',len(self.chain))
            block = {'block_number': len(self.chain) + 1,
                         'timestamp': time(),
                         'transactions': self.transactions,
                         'nonce': nonce,
                         'previous_hash': previous_hash,
                         'hash': current_hash}
            previous_hash=current_hash
            # Reset the current list of transactions
            
            self.transactions = []
            self.chain.append(block)
            print('\n\n **********8  After  self.chain.append(block)==',self.chain)
            print('len(self.chain)==',len(self.chain))
            return block
        

    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        #block_string = json.dumps(block, sort_keys=True).encode()
        #block_string = block.encode()
        block_string = json.dumps(block).encode()
        return hashlib.sha256(block_string).hexdigest()
        #return hashlib.sha1(block_string).hexdigest()

          
    def proof_of_work(self):
        """
        Proof of work algorithm
        """
        global now_hash
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce)[1] is False:
            nonce += 1
            now_hash = guess_hash

        #return nonce
        return nonce,now_hash

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        global guess
        global guess_hash
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        #return guess_hash[:difficulty] == '0'*difficulty
        return guess_hash ,guess_hash[:difficulty] == '0'*difficulty

    def valid_chain(self, chain):
        """
        check if a bockchain is valid
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            #print(last_block)
            #print(block)
            #print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            #Delete the reward transaction
            transactions = block['transactions'][:-1]
            # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
            #transaction_elements = ['sender_address', 'recipient_address', 'value']
            transaction_elements = ['sender_address', 'recipient_address', 'value_voltage','value_current','value_power','value_energy','value_datatime','value_transaction_energy']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]

            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            print('http://' + node + '/chain')
            response = requests.get('http://' + node + '/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

# Instantiate the Node
app = Flask(__name__)
CORS(app)

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/configure')
def configure():
    return render_template('./configure.html')



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
 
    # Check that the required fields are in the POST'ed data
    print('\n\n @@@@@@@@@@@@@')
    print('\n\n values = ',values )
    print('\n\n -------------  values = ' )
   #print('\n\n values amount_4=',values['amount_3'])
    required = ['sender_address', 'recipient_address', 'amount_voltage', 'amount_current', 'amount_power','amount_energy','amount_datatime','amount_transaction_energy','public_key_to_master', 'signature']
    
    print('\n\n required  = ',required  )
    if not all(k in values for k in required):
        print('\n\n k==',k)
        return 'Missing values', 400
    # Create a new Transaction
    
    transaction_result = blockchain.submit_transaction(values['sender_address'], values['recipient_address'], values['amount_voltage'], values['amount_current'],values['amount_power'],values['amount_energy'],values['amount_datatime'],values['amount_transaction_energy'],values['public_key_to_master'],values['signature'])
    #
    print('\n\ntransaction_result==')
    #print('\n\ntransaction_result :::values['amount_4']=='values['amount_4'])
    print('\n\ntransaction_result==',transaction_result)
    if transaction_result == False:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to Block '+ str(transaction_result)}
        return jsonify(response), 201

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #Get transactions from transactions pool
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.chain[-1]
    #nonce = blockchain.proof_of_work()
    #nonce = blockchain.proof_of_work()[0]
    # We must receive a reward for finding the proof.
    """
    blockchain.submit_transaction(sender_address=MINING_SENDER, recipient_address=blockchain.node_id, value=MINING_REWARD, value_current=MINING_REWARD, value_power=MINING_REWARD, value_datatime=MINING_REWARD, value_d="", signature="")
    """
    print('\n\n @@@@@ def mine()')
    """
    blockchain.submit_transaction(sender_address=MINING_SENDER, recipient_address=IP_self+':'+str(port_self), value_voltage=MINING_REWARD, value_current=MINING_REWARD, value_power=MINING_REWARD, value_datatime=MINING_REWARD,value_public_key_to_master=MINING_SENDER,signature="")
    """
    print('\n\n  def mine(): recipient_address==')
    print('\n\n  def mine():recipient_address==',blockchain.node_id)
    # Forge the new Block by adding it to the chain
    #previous_hash = blockchain.hash(last_block)
    
    #previous_hash =last_block['previous_hash']
    #previous_hash=  block['current_hash']
    #print('\n\n  def mine() previous_hash=',previous_hash)
    #current_hash = blockchain.hash(str(previous_hash) )
    # print('\n\n  def mine() current_hash=',current_hash)
    #block = blockchain.create_block(nonce, previous_hash)
    #block = blockchain.create_block(nonce)
    block = blockchain.create_block()
    print('\n\n  def mine()   block  ==',block)  
    print('\n\n  def mine()   block_number  ==',block['block_number'])
    print('\n\n  def mine()   transactions  ==', block['transactions'])
    response = {
        'message': "New Block Forged",
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash'],
        'hash': block['hash'],
    }
    return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=port_self, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host=IP_self, port=port)








