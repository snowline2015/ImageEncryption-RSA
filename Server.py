from flask import Flask, jsonify
import requests
import json

app = Flask(__name__)

f = open("database/account.txt")
accounts_list = json.loads(f.read())


@app.route('/')
def index() :
    return "fuck you"


@app.route('/account', methods=['GET'])
def get_account_list():
    return jsonify(accounts_list)


@app.route('/account/<int:account_id>', methods=['GET'])
def get_account(account_id):
    return jsonify(accounts_list[account_id])


@app.route('/account', methods=['POST'])
def create_account(account_json):
    accounts_list.append(account_json)
    return jsonify({"Created": account_json})


@app.route('/account/<int:account_id>', methods=['PUT'])
def update_account(account_id, info):
    return "fuck you"


@app.route('/account/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    accounts_list.remove(accounts_list[account_id])
    return jsonify(result="success")


if __name__ == '__main__':
    app.run(debug=True)

