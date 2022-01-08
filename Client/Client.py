import requests
import json
from Client.RSA import encrypt_image
from RSA import RSA_key_generation
from flask import Flask, render_template, url_for, request, redirect, flash
import cv2


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

        response = requests.get(url + 'login', json={"name": usrname,"password": pssword})

        response = json.loads(response.text)
        if response['status'] == "true":
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password")
    return render_template("login.html")

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        usrname = request.form.get("usrname")
        pssword = request.form.get("pssword")
        pssword2 = request.form.get("pssword2")

        if pssword != pssword2:
            flash("Confirm password does not match")
        else:
            e, n, _ = RSA_key_generation()
            
            response = requests.post(url + 'register', json={"name": usrname,"password": pssword,"id": "","pub_rsa": [e,n]})

            response = json.loads(response.text)
            if response['status'] == 'true':
                return redirect(url_for('login'))
            else:
                flash(response['status'])

    return render_template("signup.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/home", methods=['GET','POST'])
def home():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save("images/" + uploaded_file.filename)
            img = cv2.imread("/images/" + uploaded_file.filename, 0)
            img = encrypt_image(img, 15491287097074226203, 28681178489838461957)
            response = requests.post(url + "test", files={'file': (uploaded_file.filename, open(uploaded_file.filename, 'rb'))})

            response = json.loads(response.text)
            flash(response['status'])

        return redirect(url_for('home'))
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True, port=5500)
