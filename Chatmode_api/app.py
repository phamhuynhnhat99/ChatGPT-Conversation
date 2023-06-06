import os, sys
this_path = os.path.abspath(os.path.dirname(__file__))
if this_path not in sys.path:
    sys.path.append(this_path)

from flask import Flask, request

app = Flask(__name__)

from threading import Thread
import json
import time
from myDriver import MyDriver

with open("accounts.json") as acc_json:
    acc_list = json.load(acc_json)["accounts"]
    acc_json.close()

browsers = dict()
busied = dict()

def update_accounts_json():
    res = dict()
    res["accounts"] = acc_list
    accounts_path = os.path.join(this_path, "accounts.json")
    with open(accounts_path, "w") as outfile:
        json.dump(res, outfile)
    print("accounts.json has been updated...")


def create_new_browser(acc_i, name, email, passw, cookies):
    myDriver = MyDriver(name=name)
    res_cookies = myDriver.openai_login(name, email, passw, cookies)
    if res_cookies and res_cookies != "Needless":
        acc_list[acc_i]["cookies"] = res_cookies
    myDriver.skip_popups()

    browsers[acc_i] = myDriver
    busied[acc_i] = False


def get_available_browser():
    for acc_i, driver_ in browsers.items():
        if not busied[acc_i]:
            busied[acc_i] = True
            return driver_, acc_i
    return None, -1


def start():
    try:
        thr_list = []
        for acc_i, acc in enumerate(acc_list):
            name, email, passw, cookies = acc["name"], acc["email"], acc["passw"], acc["cookies"]
            thr_list.append(Thread(target=create_new_browser, args=(acc_i, name, email, passw, cookies)))

        for thr in thr_list:
            thr.start()
            time.sleep(3)

        for thr in thr_list:
            thr.join()
            time.sleep(3)
    except Exception as e:
        print(e)
    update_accounts_json()
    print(len(browsers), "browsers are currently available.")


@app.route('/', methods=['POST'])
def home():
    output = {
        "message": "Just do it."
    }
    return output, 200


@app.route('/labelling', methods=['POST'])
def labelling():
    data = request.form
    prompt = data["prompt"]

    browser, ind = get_available_browser()
    if ind == -1:
        return {"message": "All browsers are currently busy"}

    print(ind, "--> busy")
    output = {"output": browser.new_chat(prompt)}
    busied[ind] = False
    print(ind, "--> free")
    return output, 200


@app.route('/kill', methods=['POST'])
def kill():
    for browser in browsers.values():
        browser.turn_off()
    return {"message": "Goodbye."}, 200


if __name__ == '__main__':
    start()
    app.run(host="0.0.0.0", port=8081)