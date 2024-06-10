#!/bin/python

import os
from flask import Flask, render_template, url_for, redirect, flash, request, send_from_directory, send_file
from werkzeug.utils import secure_filename
from fileinput import filename
import subprocess
import shutil

APP_NAME = "AudioFileTagger"
APP_VERSION = "0.1"
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'mp3','flac'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET','POST'])
def index():
    return redirect(url_for('upload_file'))

@app.route('/upload/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            subprocess.run(['python', 'tag_script.py'])
            return redirect(url_for('download_file'))
    return render_template("index.html")

@app.route('/download/', methods = ['GET','POST'])
def download_file():
    files = os.listdir(UPLOAD_FOLDER)
    p = UPLOAD_FOLDER + '/' + files[0]
    download = send_file(p, as_attachment=True)
    for root, dirs, files in os.walk('./static/uploads/'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    return download
    

app.run(host="127.0.0.1", port=8080)
