import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from fake_useragent import UserAgent

import pandas as pd
import random
import re
op = webdriver.ChromeOptions()
op.add_argument(f"user-agent={UserAgent.random}")
op.add_argument("user-data-dir=./")
op.add_experimental_option("detach", True)
op.add_experimental_option("excludeSwitches", ["enable-logging"])

##############################
##
## op.add_argument('headless')
##
## don't show the browser (it doesn't seem to work with undetected_chromedriver) ###
## 
###############################

import json
from pathlib import Path

driver = uc.Chrome(chrome_options=op)
url = 'https://chat.openai.com'
url_login = 'https://chat.openai.com/auth/login/'

url_test = "https://chat.openai.com/chat/9505dbcb-53b4-4859-a448-e97964cba7f3"

uname = "bimnaxu753@gmail.com"
passw = "Singapore#2708"


def refresh(url_=url, wait_time_=4):
    driver.get(url_)
    time.sleep(wait_time_)


def bypassCloudfare():
    pass


cookies_path = "cookies.json"
def save_cookie():
    Path(cookies_path).write_text(
        json.dumps(driver.get_cookies(), indent=2)
    )
    print("Save success")


def load_cookie():
    load = False
    cookies = json.loads(Path(cookies_path).read_text())
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
            load = True
        except:
            continue
    print("Load success")
    return load


def openai_login(MAIL, PASSWORD):
    # Try to log in with cookies
    load = False
    try:
        refresh(url_=url, wait_time_=4)
        driver.delete_all_cookies()
        load = load_cookie()
        if load:
            time.sleep(1)
            refresh(url_=url, wait_time_=4)
    except Exception as e:
        print("Error occurred when trying to login:", e)
    
    if not load:
        print("Need Log in")
        refresh(url_=url_login, wait_time_=10)
        inputElements = driver.find_elements(By.TAG_NAME, "button")
        inputElements[0].click()
        time.sleep(10)

        mail = driver.find_elements(By.TAG_NAME, "input")[1]
        mail.send_keys(MAIL)
        btn=driver.find_elements(By.TAG_NAME, "button")[0]
        btn.click()

        password= driver.find_elements(By.TAG_NAME,"input")[2]
        password.send_keys(PASSWORD)
        btn=driver.find_elements(By.TAG_NAME,"button")[1]
        btn.click()
        
        time.sleep(3)
        save_cookie()

    
def skip_popups():
    tmp = 0
    cls_n = "//button[@class='btn relative btn-neutral ml-auto']"
    while True:
        skip=driver.find_elements(By.XPATH, cls_n)
        if len(skip) > 0:
            skip[0].click()
            tmp += 1
        if tmp == 2:
            cls_n = "//button[@class='btn relative btn-primary ml-auto']"
        if tmp == 3:
            break
        time.sleep(2)

    print("Logging success!!!")
    refresh(url_=url_test, wait_time_=4)


def get_response(prompt):

    def filter_text(text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    prompt = filter_text(text=prompt)


    def check_too_many_requests():
        over = False
        cls_n = "//div[@class='flex flex-grow flex-col gap-3']"
        many_requests_alert = driver.find_elements(By.XPATH, cls_n)
        if len(many_requests_alert):
            lastText = many_requests_alert[-1].text

            _1st_alert = "Too many requests in 1 hour."
            _2nd_alert = "Something went wrong."
            _3rd_alert = "An error occurred."
            if _1st_alert in lastText or _2nd_alert in lastText or _3rd_alert in lastText:
                over = True
        return over

    def send_input():
        inputElements = driver.find_elements(By.TAG_NAME, "textarea")
        inputElements[0].send_keys(prompt)
        driver.implicitly_wait(2)
        
        btnElements = driver.find_elements(By.TAG_NAME, "button")
        btnElements[-1].click()
        time.sleep(3)

    def get_output():
        output = "Unknown"
        kill_time = 0
        max_kill_time = 180
        while kill_time < max_kill_time:
            try:
                outputElements = driver.find_elements(By.XPATH, cls_n)
                output = outputElements[-1].text
                kill_time = max_kill_time
            except Exception as e:
                print("Error occurred when trying to get ChatGPT's answer")
                kill_time += 3
                refresh(url_=url_test, wait_time_=3)
        return output

    cls_n = "//div[@class='markdown prose w-full break-words dark:prose-invert light']"
    stop_generate_btn_class = "//button[@class='btn relative btn-neutral border-0 md:border']"

    send_input()

    while check_too_many_requests():
        time_out = random.randint(5, 15)
        message = "Waiting for " + str(time_out) + " minutes!!!"
        print(message)
        time.sleep(time_out*60)

        refresh(url_=url_test, wait_time_=4)
        send_input()

    kill_time = 0
    max_kill_time = 200
    while kill_time < max_kill_time:
        btnText = driver.find_elements(By.XPATH, stop_generate_btn_class)
        if len(btnText) and btnText[0].text == "Regenerate response":
            kill_time = max_kill_time
        time.sleep(3)
        kill_time += 3

    response = get_output()

    return response


def get_list_of_comments(csv_path="test.csv"):
    df = pd.read_csv(csv_path)
    short_cmt_df = df["content"]
    return list(short_cmt_df)


def run():
    openai_login(uname, passw)
    skip_popups()
 
    result_list = []
    prefix = 'Hãy đánh nhãn câu '
    suffix = '. Trả lời trắc nghiệm, chỉ chọn 1 trong 4 nhãn: Positive, Negative, Neutral, Unknown và không cần nói thêm'
    
    test_list = get_list_of_comments()

    for i, cmt in enumerate(test_list):
        if i >= 500:
            prompt = prefix + '"' + cmt + '"' + suffix
            try:
                response = get_response(prompt)
            except Exception as e:
                print("Error of this text", prompt)
                print("Error occurred when trying to request:", e)
                response = "Unknown"
                refresh(url_=url_test, wait_time_=4)

            result_list.append(response)

            time_out = random.randint(13, 19)
            try:
                if len(result_list)==50:
                    time_out = random.randint(60, 120)

                    df = pd.DataFrame(result_list, columns=["Label"])
                    name = "label_" + str(i//50) + ".csv"
                    df.to_csv(name)
                    result_list = []
            except Exception as e:
                print(e)

            time_out = random.randint(1, 3)
            time.sleep(time_out)

    if len(result_list) > 0:
        df = pd.DataFrame(result_list, columns=["Label"])
        name = "label_remainder" + ".csv"
        df.to_csv(name)
    
    driver.close()


if __name__ == "__main__":
    run()