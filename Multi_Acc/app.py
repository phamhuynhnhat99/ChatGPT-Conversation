import os
import sys
import json
from threading import Thread
import time

import pandas as pd

Multi_Acc_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(Multi_Acc_path)
from myDriver import MyDriver as Browser

with open("accounts.json") as acc_json:
    acc_list = json.load(acc_json)["accounts"]
    acc_json.close()

# ---------------------------------------------------------------------------

def filter_csv(input_file):
    df = pd.read_csv(input_file, dtype=str, keep_default_na=False)
    # Pre-processing
    labels = list(df.label.unique())
    selected_labels = []
    for label in labels:
        tmp = df[df["label"] == label]
        if len(tmp) > 0:
            selected_labels.append(label)
    df = df.loc[df["label"].isin(selected_labels)]
    int_label = [int(float(_)) for _ in df.label]
    df["label"] = int_label

    # df_0 = df[df["label"] == 0].sample(n=30)
    # df_1 = df[df["label"] == 1].sample(n=30)
    # df_2 = df[df["label"] == 2].sample(n=30)
    # df_3 = df[df["label"] == 3].sample(n=30)
    # df_4 = df[df["label"] == 4].sample(n=30)
    # df_5 = df[df["label"] == 5].sample(n=30)
    # df_6 = df[df["label"] == 6].sample(n=30)
    # df_7 = df[df["label"] == 7].sample(n=30)
    
    # df_x = pd.DataFrame()
    # df_x = pd.concat([df_0, df_1, df_2, df_3, df_4, df_5, df_6, df_7], axis=0)
    # df_x.to_csv("sales_x30.csv", index=False)
    return df


def update_accounts_json():
    res = dict()
    res["accounts"] = acc_list
    accounts_path = Multi_Acc_path + "/accounts.json"
    with open(accounts_path, "w") as outfile:
        json.dump(res, outfile)
    print("accounts.json has been updated...")


def new_browser(acc_i, name, email, passw, cookies, big_df, from_ind, to_ind):
    myDriver = Browser(name=name)
    res_cookies = myDriver.openai_login(name, email, passw, cookies)
    if res_cookies and res_cookies != "Needless":
        acc_list[acc_i]["cookies"] = res_cookies
    myDriver.skip_popups()
    myDriver.new_chat()
    myDriver.get_answer(big_df, from_ind, to_ind)


def run():
    big_df = filter_csv("/home/aia/Nhat/ChatGPT-Conversation/Multi_Acc/sales_x30_manual.csv")
    print("CSV had been read.")
    from_inds = [0, 120]
    to_inds = [119, 239]
    try:
        thr_list = []
        for acc_i, acc in enumerate(acc_list):
            name, email, passw, cookies = acc["name"], acc["email"], acc["passw"], acc["cookies"]
            thr_list.append(Thread(target=new_browser, args=(acc_i, name, email, passw, cookies, big_df, from_inds[acc_i], to_inds[acc_i])))

        for thr in thr_list:
            thr.start()
            time.sleep(2)

        for thr in thr_list:
            thr.join()
            time.sleep(2)
    except Exception as e:
        print(e)

    update_accounts_json()


if __name__ == '__main__':
    run()