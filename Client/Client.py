import requests
import json
from RSA import RSA_key_generation, encrypt_image, decrypt_image
from flask import Flask, render_template, url_for, request, redirect, flash
from PIL import Image
import numpy as np
import io
import base64
import cv2


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
    return render_template("home.html", files=response, user=username)

@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
            uploaded_file.save("images/" + uploaded_file.filename)
            img, shape, enc = encrypt_image('images/' + uploaded_file.filename, int(pub_rsa[0]), int(pub_rsa[1]))

            imgByteArr = cv2.imencode('.jpg', img)[1].tostring()
            imgByteArr = base64.b64encode(imgByteArr)

            enc = np.array(enc)
            enc_str = str(shape[0]) + ';' + str(shape[1]) + ';' + str(enc.shape[0]) + ';' + str(enc.shape[1]) + ';'
            for i in range(enc.shape[0]):
                for j in range(enc.shape[1]):
                    enc_str += str(enc[i][j]) + ';'

            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            payload = json.dumps({"image": imgByteArr.decode('utf-8'), "filename": uploaded_file.filename, "username": username, "enc": enc_str})
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
    if request.method == 'POST':
        response = requests.get(url + username + '/images', auth=(username, password))
        response = json.loads(response.text)
        pri_key = []
        for f in response:
            if "_share_key.txt" in f[0]:
                temp = f[0].replace("_share_key.txt", "")
                res = requests.get(url + username + '/images/download/' + f[0], auth=(username, password))
                res = json.loads(json.loads(res.text))
                pri_key.append(int(res[0]))
                pri_key.append(int(res[1]))
                response.remove(f)

                for k in response:
                    if (temp + "_enc.txt") in k[0]:
                        res = requests.get(url + username + '/images/download/' + k[0], auth=(username, password))
                        res = json.loads(res.text)

                        res = res['enc'].split(';')
                        count = 4
                        enc = [[0 for x in range(int(res[3]))] for y in range(int(res[2]))]
                        for i in range(int(res[2])):
                            for j in range(int(res[3])):
                                if '[' in res[count]:
                                    res[count] = res[count].replace('[', '')
                                    res[count] = res[count].replace(']', '')
                                    enc[i][j] = [int(i) for i in res[count].split(',')]
                                else:
                                    enc[i][j] = int(res[count])
                                count += 1

                        img = decrypt_image((int(res[0]), int(res[1])), enc, int(pri_key[0]), int(pri_key[1]))
                        for files in response:
                            if f[0].split('_')[0] in files[0]:
                                cv2.imwrite('images/' + files[0], img)
                                break
                        response.remove(k)
        for f in response:
            if '_enc.txt' in f[0]:
                res = requests.get(url + username + '/images/download/' + f[0], auth=(username, password))
                res = json.loads(res.text)
                # img = base64.b64decode(res['image'].encode('utf-8'))

                res = res['enc'].split(';')
                count = 4
                enc = [[0 for x in range(int(res[3]))] for y in range(int(res[2]))]
                for i in range(int(res[2])):
                    for j in range(int(res[3])):
                        if '[' in res[count]:
                            res[count] = res[count].replace('[', '')
                            res[count] = res[count].replace(']', '')
                            enc[i][j] = [int(i) for i in res[count].split(',')]
                        else:
                            enc[i][j] = int(res[count])
                        count += 1

                img = decrypt_image((int(res[0]), int(res[1])), enc, int(priv_rsa[0]), int(priv_rsa[1]))
                for files in response:
                    if f[0].split('_')[0] in files[0]:
                        cv2.imwrite('images/' + files[0], img)
                        break
        flash("Downloaded all images")
    return redirect(url_for('home'))


@app.route("/share", methods=['GET','POST'])
def share():
    if request.method == 'POST':
        user_id = request.form.get('user-id')
        filename = request.form.get('user-file')
        if user_id == "" or filename == "":
            flash("All field must not be empty")
            return redirect(url_for('home'))
        response = requests.post(url + username + '/images/share', json={"id": user_id, "filename": filename}, auth=(username, password))
        response = json.loads(response.text)
        if response['status'] != 'true':
            flash(response['status'])
    return redirect(url_for('home'))



@app.route("/download", methods=['GET','POST'])
def download():
    pass


@app.route("/logout", methods=['GET','POST'])
def logout():
    response = requests.post(url + 'logout', auth=(username, password))
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True, port=5500)
