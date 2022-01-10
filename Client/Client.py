import requests
import json
from RSA import RSA_key_generation, encrypt_image, decrypt_image
from flask import Flask, render_template, url_for, request, redirect, flash
from PIL import Image
import numpy as np
import io
import base64


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supremestrange'
url = 'http://127.0.0.1:5000/'

username = ''
password = ''
pub_rsa = None
priv_rsa = None

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        global username, password
        username = usrname
        password = pssword

        response = requests.get(url + 'login', json={"name": usrname,"password": pssword})

        response = json.loads(response.text)
        if 'status' in response and response['status'] == "false":
            flash("Incorrect username or password")
        else:
            global pub_rsa, priv_rsa
            pub_rsa = response["pub_rsa"]
            priv_rsa = response["priv_rsa"]
            return redirect(url_for('home'))
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
            e, n, d = RSA_key_generation()
            
            response = requests.post(url + 'register', json={"name": usrname,"password": pssword,"id": "",
                                                             "pub_rsa": [e,n], "priv_rsa": [d,n]})

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
    response = requests.get(url + username + '/images', auth=(username, password))
    response = json.loads(response.text)
    for f in response:
        if ".txt" in f[0]:
            response.remove(f)
    return render_template("home.html", files=response)

@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
            uploaded_file.save("images/" + uploaded_file.filename)
            img = np.array((Image.open('images/' + uploaded_file.filename).convert('L')))
            img = encrypt_image(img, int(pub_rsa[0]), int(priv_rsa[1]))

            imgByteArr = io.BytesIO()
            img.save(imgByteArr, format='PNG')
            imgByteArr = imgByteArr.getvalue()
            imgByteArr = base64.b64encode(imgByteArr)

            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            payload = json.dumps({"image": imgByteArr.decode('utf-8'), "filename": uploaded_file.filename, "username": username})
            response = requests.post(url + "upload", data=payload, headers=headers, auth=(username, password))

            response = json.loads(response.text)
            flash(response['status'])
        else:
            flash("Wrong file type chosen")
            return redirect(url_for('upload'))

        return redirect(url_for('home'))
    return render_template("upload.html")


@app.route("/download-all", methods=['GET','POST'])
def download_all():
    response = requests.get(url + username + '/images', auth=(username, password))
    response = json.loads(response.text)
    temp = '.txt'
    pri_key = []
    for f in response:
        if ".txt" in f[0]:
            temp = f[0].replace(".txt", "")
            res = requests.get(url + username + '/images/download/' + f[0], auth=(username, password))
            res = json.loads(res.text)
            for i in res:
                pri_key.append(i)
            response.remove(f)
        if temp in f[0]:
            res = requests.get(url + username + '/images/download' + f[0], auth=(username, password))
            res = json.loads(res.text)
            img = np.array(Image.open(io.BytesIO(res['image'].encode())).convert('L'))
            img = decrypt_image(img, int(pri_key[0]), int(pri_key[1]))
            img.save("images/" + f[0])
            response.remove(f)
    for f in response:
        res = requests.get(url + username + '/images/download' + f[0], auth=(username, password))
        res = json.loads(res.text)
        img = np.array(Image.open(io.BytesIO(res['image'].encode())).convert('L'))
        img = decrypt_image(img, int(pri_key[0]), int(pri_key[1]))
        img.save("images/" + f[0])
    return flash("Downloaded all images")


# @app.route("/share", methods=['GET','POST'])
# def share():
#     if request.method == 'POST':


@app.route("/logout", methods=['GET','POST'])
def logout():
    response = requests.post(url + 'logout')
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, port=5500)
