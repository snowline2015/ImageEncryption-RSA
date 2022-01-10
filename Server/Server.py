from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
import json
from PIL import Image
import io
import base64
import os
import shutil

app = Flask(__name__)


auth = HTTPBasicAuth()
@auth.verify_password
def verify_password(username, password):
    for account in accounts_list:
        if account['name'] == username:
            return account['password'] == password
    return False


accounts_list = json.loads(open("database/account.txt").read())


@app.route('/')
def index():
    return "Things just got out of hand - Supreme Strange"


# @app.route('/account', methods=['GET'])
# def get_account_list():
#     return jsonify(accounts_list)


# @app.route('/account/<int:account_id>', methods=['GET'])
# def get_account(account_id):
#     return jsonify(accounts_list[account_id])


@app.route('/register', methods=['POST'])
def register():
    new_account = request.get_json()
    sum = 0
    for account in accounts_list:
        if account['name'] == new_account['name']:
            return jsonify({"status": "Account already exists"})
        sum += int(account['id']) + 1

    n = len(accounts_list)
    total = (n + 1) * (n + 2) / 2
    new_account['id'] = int(total - sum - 1)

    accounts_list.append(new_account)
    with open("database/account.txt", 'w') as f:
        json.dump(accounts_list, f, indent=4)
    return jsonify({"status": "true"})


# @app.route('/account/<int:account_id>', methods=['PUT'])
# def update_account(account_id, info):
#     return "fuck you"


# @app.route('/account/<int:account_id>', methods=['DELETE'])
# def delete_account(account_id):
#     temp = accounts_list[account_id]
#     accounts_list.remove(accounts_list[account_id])
#     with open("database/account.txt", 'w') as f:
#         json.dump(accounts_list, f, indent=4)
#     return jsonify({"Deleted": temp})


@app.route('/login', methods=['GET'])
def login():
    login_account = request.get_json()
    for account in accounts_list:
        if account['name'] == login_account['name'] and account['password'] == login_account['password']:
            return jsonify({"status": "true"})
    return jsonify({"status": "false"})


@app.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def upload_image():
    if not request.json or 'image' not in request.json:
        return jsonify({"status": "false"})

    img = request.json['image']
    img = base64.b64decode(img.encode('utf-8'))
    img = Image.open(io.BytesIO(img))

    path = 'database/images/' + request.json['username']
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    img.save(path + '/' + request.json['filename'])
    return jsonify({"status": "true"})


@app.route('/<username>/images', methods=['GET'])
@auth.login_required
def get_images_list(username):
    path = 'database/images/' + username
    isExist = os.path.exists(path)
    if not isExist:
        return jsonify([['no image','']])
    files = os.listdir(path)
    lst = []
    for f in files:
        lst.append([f, str(round(os.path.getsize(path + '/' + f) / 1024, 2))])
    return jsonify(lst)


@app.route('/<username>/images/<filename>', methods=['GET'])
@auth.login_required
def get_image(username, filename):
    path = 'database/images/' + username
    isExist = os.path.exists(path)
    if not isExist:
        return jsonify({"status": "false"})
    with open(path + '/' + filename, 'rb') as f:
        image = f.read()
    return jsonify(image)


@app.route('/<username>/images/share', methods=['POST'])
@auth.login_required
def share_image(username):
    share_info = request.get_json()
    for account in accounts_list:
        if account['id'] == share_info['id']:
            path = 'database/images/' + account['name']
            isExist = os.path.exists(path)
            if not isExist:
                os.makedirs(path)
            shutil.copyfile('database/images/' + username + '/' + share_info['filename'],
                            path + '/' + share_info['filename'])
            return jsonify({"status": "true"})
    return jsonify({"status": "Cannot find account with id"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)


