from flask import Flask, jsonify, request
import json

app = Flask(__name__)

accounts_list = json.loads(open("database/account.txt").read())


@app.route('/')
def index() :
    return "Things just got out of hand - Supreme Strange"


@app.route('/account', methods=['GET'])
def get_account_list():
    return jsonify(accounts_list)


@app.route('/account/<int:account_id>', methods=['GET'])
def get_account(account_id):
    return jsonify(accounts_list[account_id])


@app.route('/account', methods=['POST'])
def create_account():
    new_account = request.get_json()
    sum = 0
    for account in accounts_list:
        if account['name'] == new_account['name']:
            return jsonify({"Error": "Account already exists"})
        sum += int(account['id']) + 1

    n = len(accounts_list)
    total = (n + 1) * (n + 2) / 2
    new_account['id'] = total - sum - 1

    accounts_list.append(new_account)
    with open("database/account.txt", 'w') as f:
        json.dump(accounts_list, f, indent=4)
    return jsonify({"Created": new_account})


@app.route('/account/<int:account_id>', methods=['PUT'])
def update_account(account_id, info):
    return "fuck you"


@app.route('/account/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    temp = accounts_list[account_id]
    accounts_list.remove(accounts_list[account_id])
    with open("database/account.txt", 'w') as f:
        json.dump(accounts_list, f, indent=4)
    return jsonify({"Deleted": temp})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=50000)

