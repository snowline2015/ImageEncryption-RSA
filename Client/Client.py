import requests
import json
from RSA import RSA_key_generation

url = 'http://127.0.0.1:5000/'

# Get all account
response = requests.get(url + 'account')

# Get specific account
response = requests.get(url + 'account/0')

# Register account
account = {"name": "iamjusthoang","pass": "123","id": "","pub_rsa": ["",""]}
response = requests.post(url + 'account', json=account)

# Update account
account = {"name": "iamjusthoang","pass": "123","id": "","pub_rsa": ["",""]}
response = requests.put(url + 'account/0', json=account)

# Delete account
response = requests.delete(url + 'account/1')


print(response.text)