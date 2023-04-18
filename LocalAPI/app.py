import os
import sys
from flask import Flask, request, jsonify

LocalAPI_path = os.path.abspath(__file__)
sys.path.append(LocalAPI_path)
from myDriver import MyDriver as Browser

myDriver = Browser()
myDriver.openai_login()
myDriver.skip_popups()

app = Flask(__name__)

@app.route('/')
def hello():
    return 200, {'Hello, World!'}


@app.route('/newchat')
def newChat():
    
    return 200, {'Hello, World!'}


@app.route('/extract', methods=['POST'])
def extract():
    input_file = request.files['input_file']
    input_text = input_file.read().decode('utf-8')
    response = myDriver.get_answer(input_text)
    return jsonify(response)


@app.get('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    myDriver.close()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)