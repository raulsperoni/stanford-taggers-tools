#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stanford_server as stanford
import socket, os
from flask import Flask,jsonify,request
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['tsv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.environ['STANFORD_NER_FOLDER'],'classifiers'))

ner_process = None
pos_process = None
ner_train_process = None
ner_train_filename = None



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/ner/start/<model>')
def ner_start(model):
    global ner_process
    if not ner_process:
        (ner_process,themodel,theport) = stanford.start_ner_server(model)
        return jsonify(message='Iniciando Stanford NER server',
                       host=socket.gethostbyname(socket.gethostname()),
                       port=theport,
                       model=themodel)
    else: 
        return jsonify(message='Esta iniciado')

@app.route('/ner/stop')
def ner_stop():
    global ner_process
    if ner_process:
        ner_process.terminate()
        ner_process.kill()
        ner_process = None
        return jsonify(message='Deteniendo Stanford NER server')
    else:
        return jsonify(message='No esta iniciado')
        
@app.route('/ner/status')
def ner_status():
    if ner_process and not ner_process.poll():
        return jsonify(status='ON')
    elif ner_process:
        return jsonify(status='OFF',code=ner_process.returncode)
    else:
        return jsonify(status='OFF')

@app.route('/pos/start')
def pos_start():
    global pos_process
    if not pos_process:
        (pos_process,themodel,theport) = stanford.start_pos_server()
        return jsonify(message='Iniciando Stanford POS server',
                       host=socket.gethostbyname(socket.gethostname()),
                       port=theport,
                       model=themodel)
    else: 
        return jsonify(message='Esta iniciado')

@app.route('/pos/stop')
def pos_stop():
    global pos_process
    if pos_process:
        pos_process.terminate()
        pos_process.kill()
        pos_process = None
        return jsonify(message='Deteniendo Stanford POS server')
    else:
        return jsonify(message='No esta iniciado')
        
@app.route('/pos/status')
def pos_status():
    if pos_process and not pos_process.poll():
        return jsonify(status='ON')
    elif pos_process:
        return jsonify(status='OFF',code=pos_process.returncode)
    else:
        return jsonify(status='OFF')


        
@app.route("/ner/train", methods=['GET', 'POST'])
def ner_train():
    global ner_train_filename
    global ner_train_process
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ner_train_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.chmod(ner_train_filename, 0o777)
            return jsonify(status='OK')
        else:
            return jsonify(status='ERROR',message='Error con el archivo')
    else: 
        if ner_train_filename and not ner_train_process:
            (ner_train_process,cmd) = stanford.do_ner_train(ner_train_filename)
            out, err = ner_train_process.communicate()
            thestatus = ner_train_process.wait()
            ner_train_process = None
            return jsonify(command=cmd,message=out,error=err,status=thestatus)
        elif not ner_train_filename:
            return jsonify(status='ERROR',message='Debe enviar archivo de entrenamiento')
    return jsonify(status='ERROR')
    
@app.route("/ner/models", methods=['GET'])
def ner_models():
    path = os.path.abspath(os.path.join(os.environ['STANFORD_NER_FOLDER'],'classifiers'))
    res = []
    for file_name in os.listdir(path):
        if '.gz' in file_name:
            res.append(file_name)
        
    return jsonify(models=res)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',threaded=True)
    """while True:
        if ner_process:
            out = ner_process.stderr.readline()
            if out and out != "":
            	print out
            out = ner_process.stdout.readline()
            if out and out != "":
                print out
        if pos_process:
            out = pos_process.stderr.readline()
            if out and out != "":
                print out
            out = pos_process.stdout.readline()
            if out and out != "":
                print out"""


