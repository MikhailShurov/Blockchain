import hashlib
import json
from flask import Flask, jsonify, request
from time import time
from uuid import uuid4


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,                  #Тут должен быть хэш корня Меркла
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
        pass


    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1
        pass

    # @staticmethod
    # def hash(block):
    #     block_string = json.dumps(block, sort_keys=True).encode()
    #     return hashlib.sha256(block_string).hexdigest()
    #     pass
    #
    # @property
    # def last_block(self):
    #     print(len(self.chain))
    #     return self.chain[-1]
    #     pass
    #
    # def proof_of_work(self, last_proof):
    #     proof = 0
    #     while self.valid_proof(last_proof, proof) is False:
    #         proof += 1
    #     return proof
    #
    # @staticmethod
    # def valid_proof(last_proof, proof):
    #     guess = f'{last_proof}{proof}'.encode()
    #     guess_hash = hashlib.sha256(guess).hexdigest()
    #     return guess_hash[:4] == "0000"


# app = Flask(__name__)
# node_identifier = str(uuid4()).replace('-', '')
# blockchain = Blockchain()


# @app.route('/mine', methods=['GET'])
# def mine():
#     # #Мы запускаем алгоритм PoW для того чтобы найти следующий proof...
#     # last_block = blockchain.last_block
#     # last_proof = last_block['proof']
#     # proof = blockchain.proof_of_work(last_proof)
#
#
#     # Мы должны получить награду за найденный proof.
#     # Если sender = "0", то это означает что данный узел заработал биткойн.
#     # blockchain.new_transaction(
#     #     sender="0",
#     #     recipient=node_identifier,
#     #     amount=1,
#     # )
#
#
#     # Формируем новый блок, путем добавления его в цепочку
#     block = blockchain.new_block(proof)
#
#     response = {
#         'message': "New Block Forged",
#         'index': block['index'],
#         'transactions': block['transactions'],
#         'proof': block['proof'],
#         'previous_hash': block['previous_hash'],
#     }
#     return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # values = request.get_json()
    # # Проверяем, что обязательные поля переданы в POST-запрос
    # required = ['sender', 'recipient', 'amount']
    # if not all(k in values for k in required):
    #     return 'Missing values', 400

    # Создаем новую транзакцию
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)