import requests
import json
from RSA import RSA_key_generation
from flask import Flask, render_template, url_for, request, redirect, flash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supremestrange'
url = 'http://127.0.0.1:5000/'

# # Get all account
# response = requests.get(url + 'account')

# # Get specific account
# response = requests.get(url + 'account/0')

# # Register account
# account = {"name": "iamjusthoang","pass": "123","id": "","pub_rsa": ["",""]}
# response = requests.post(url + 'account', json=account)

# # Update account
# account = {"name": "iamjusthoang","pass": "123","id": "","pub_rsa": ["",""]}
# response = requests.put(url + 'account/0', json=account)

# # Delete account
# response = requests.delete(url + 'account/1')


@app.route("/", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usrname = request.form.get("usrname")
        pssword = request.form.get("pssword")

        response = requests.get(url, json={"name": usrname,"pass": pssword})

        if response == True:
            return redirect("home")
        else:
            flash("Incorrect username or password")
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/home")
def home():
    return redirect("home.html")

if __name__ == "__main__":
    app.run(debug=True, port=5500)
