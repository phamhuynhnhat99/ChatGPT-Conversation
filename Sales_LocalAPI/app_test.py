import os
import sys
from flask import Flask, request, jsonify

LocalAPI_path = os.path.abspath(__file__)
sys.path.append(LocalAPI_path)
from myDriver import MyDriver as Browser

myDriver = Browser()
myDriver.openai_login()
myDriver.skip_popups()
# myDriver.new_chat()

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello world!'}, 200


@app.route('/newchat', methods=['POST', 'GET'])
def newchat():
    myDriver.new_chat()
    return {'message': 'Hi there!'}, 200


@app.route('/extract', methods=['POST'])
def extract():
    input_file = request.files['input_file']
    response = myDriver.get_answer(input_file)
    return jsonify(response), 200


@app.get('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    myDriver.close()
    return 'Server shutting down...'

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    
    myDriver.get_answer("/home/aia/Nhat/ChatGPT-Conversation/Sales_LocalAPI/sales.csv")