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

freeDrivers = [] # queue

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
    freeDrivers.append(myDriver)


def start():
    print("Loading ...")
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
    print(len(freeDrivers), "browsers are currently available.")


@app.route('/', methods=['POST'])
def home():
    output = {
        "output": "Just do it."
    }
    return output, 200

@app.route('/kill', methods=['POST'])
def kill():
    for driver in freeDrivers:
        driver.turn_off()
    output = {
        "output": "Goodbye."
    }
    return output, 200


@app.route('/labeling', methods=['POST'])
def labeling():
    
    def get_available_driver():
        if len(freeDrivers) == 0:
            return None
        freeDriver = freeDrivers[0]
        freeDrivers.pop(0)
        return freeDriver
    
    def try_it(prompt, num_time):
        if num_time == len(freeDrivers):
            return "All browsers are currently busy", None
        
        freeDriver = get_available_driver()
        num_time += 1
        
        if not freeDriver:
            freeDrivers.append(freeDriver)
            return "All browsers are currently busy", None
        print(freeDriver.name, "--> busy")
        try:
            gpt_response = freeDriver.new_chat(prompt)
            freeDriver_clone = freeDriver
        except Exception as e:
            print(freeDriver.name, ": Error occuring while request")
            gpt_response = e
        if gpt_response is None: # over
            freeDrivers.append(freeDriver)
            print("try do it with another.")
            return try_it(prompt, num_time)
        return gpt_response, freeDriver_clone
        
    data = request.form
    prompt = data["prompt"]

    num_time = 0
    gpt_response, freeDriver_clone = try_it(prompt, num_time)
      
    output = {"output": gpt_response}
    if freeDriver_clone is not None:
        freeDrivers.append(freeDriver_clone)
        print(freeDriver_clone.name, "--> free")
    return output, 200


if __name__ == '__main__':
    start()
    app.run(host="0.0.0.0", port=8081)