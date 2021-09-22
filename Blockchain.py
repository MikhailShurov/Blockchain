from time import time
from hashlib import sha256
from flask import Flask, jsonify, request
import json
from urllib.parse import urlparse
import requests

app = Flask(__name__)
node_identifier = 12345


class Blockchain(object):

    def __init__(self):
        self.transactions = []
        self.chain = []
        self.mining_points = set()


    def find_merkle_root(self, trans):
        transactions = trans.copy()
        length = len(transactions)
        if length % 2 != 0:
            transactions.append(transactions[len(transactions)-1])
        i = 0
        while i < len(transactions):
            encoded_string = str(transactions[i]).encode()
            hashed_string = sha256(encoded_string).hexdigest()
            second_encoded_string = str(transactions[i+1]).encode()
            second_hashed_string = sha256(second_encoded_string).hexdigest()
            sum_and_hashed_string = hashed_string + second_hashed_string
            transactions[i] = sha256(sum_and_hashed_string.encode()).hexdigest()
            del transactions[i+1]
            i += 1
        if len(transactions) > 2:
            self.find_merkle_root(transactions)
        if(len(transactions) == 2):
            return sha256((str(transactions[0]) + str(transactions[1])).encode()).hexdigest()


    def new_transaction(self, sender, recipient, amount):
        current_transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.transactions.append(current_transaction)


    def new_block(self, num, merkle_root):
        if len(self.chain) != 0:
            previous_hash = self.chain[-1]['hash']
        else:
            previous_hash = '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'
        height = len(self.chain)
        current_block = {
            'height': height,
            'time': time(),
            'previous_hash': previous_hash,
            'num': num,
            'hash': '',
            'transactions_amount': len(self.transactions),
            'merkle_root': merkle_root,
            'transactions': self.transactions
        }
        hash = sha256(json.dumps(current_block).encode()).hexdigest()
        self.chain.append(current_block)
        self.chain[-1]['hash'] = hash
        self.transactions = []
        return 'Block successfully hashed and added'


    def add_new_mining_point(self, address):
        parsed_url_address = urlparse(address)
        self.mining_points.add(parsed_url_address.netloc)


    def check_chain_for_valid(self, chain):
        index_of_block_in_chain = 1
        while index_of_block_in_chain < len(chain):
            previous_block_true_hash = chain[index_of_block_in_chain-1]['hash']
            current_block_previous_hash = chain[index_of_block_in_chain]['previous_hash']
            if previous_block_true_hash != current_block_previous_hash:
                return False
            if get_new_right_hash_with_previous(current_block_previous_hash, chain[index_of_block_in_chain-1]['hash']) == False:
                return False
            index_of_block_in_chain += 1
        return True


    def make_consensus(self):
        all_mining_points = self.mining_points
        new_right_chain = None
        our_blockchain_length = len(self.chain)
        print(len(all_mining_points))
        for point in all_mining_points:
            print(str(point))
            response = requests.get('http://'+ str(point) +'/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > our_blockchain_length and self.check_chain_for_valid(chain):
                    our_blockchain_length = length
                    new_right_chain = chain
        if new_right_chain:
            self.chain = new_right_chain
            return True
        return False


def get_new_right_hash_with_previous(previous, number):
    guess = f'{previous}{number}'.encode()
    guess_hash = sha256(guess).hexdigest()
    return str(guess_hash)[:4] == "0000"


def get_two_num_for_generate_hash(previous_hash):
    num = 0
    while get_new_right_hash_with_previous(previous_hash, num) == False:
        num += 1
    return num


blockchain = Blockchain()


@app.route('/mining', methods=['POST'])
def mining():
    if(len(blockchain.chain) != 0):
        last_block_hash = blockchain.chain[-1]
    else:
        last_block_hash = '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'        # Хэш от нуля
    print(last_block_hash)
    required_number = get_two_num_for_generate_hash(last_block_hash)
    print(required_number)
    merkle_root = blockchain.find_merkle_root(blockchain.transactions)
    blockchain.new_transaction(0, node_identifier, 1)
    blockchain.new_block(required_number, merkle_root)
    response = 'All\'s done successfully! ' + 'Chain length is ' + str(len(blockchain.chain))
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def show_chain():
    response = {
        'chain_length': str(len(blockchain.chain)),
        'chain': blockchain.chain
    }
    return jsonify(response), 200


@app.route('/transactions/add', methods=['POST'])
def add_new_transaction():
    values = request.get_json()
    required_values = ['sender', 'recipient', 'amount']
    if ('sender' in values) and ('recipient' in values) and ('amount' in values):
        if (values['sender'] == "") or (values['recipient'] == "") or (values['amount'] == ""):
            wrong_req = 'Something went wrong, try again'
            return jsonify(wrong_req), 404
    blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    successfully_req = 'New transaction successfully added'
    return jsonify(successfully_req), 200


@app.route('/transactions', methods=['POST'])
def show_transactions():
    transactions = blockchain.transactions
    return jsonify(transactions), 200


@app.route('/registration-new-mining-point', methods=['POST'])
def registration_new_point():
    val = request.get_json()
    new_mining_point_address = val['nodes']
    if new_mining_point_address == None:
        req = 'Impossible to found new point address. Please try again'
        return jsonify(req), 404
    for point in new_mining_point_address:
        blockchain.add_new_mining_point(point)
    req = 'New mining points has been added successfully'
    return jsonify(req), 200


@app.route('/parse-new-right-chain', methods=['POST'])
def consensus():
    new_right_chain = blockchain.make_consensus()

    if new_right_chain:
        response = {
            'message': 'New chain has been successfully replace',
            'chain': blockchain.chain
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Our chain is correct',
            'chain': blockchain.chain
        }
        return jsonify(response), 404


@app.route('/show-nodes', methods=['POST'])
def show_nodes():
    response = {
        'nodes': list(blockchain.mining_points)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
    blockchain = Blockchain()
    # previous_hash = '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'