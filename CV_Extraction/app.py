import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from fake_useragent import UserAgent

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import random
import re

op = webdriver.ChromeOptions()
op.add_argument('--headless=new')
op.add_argument(f"user-agent={UserAgent.random}")
op.add_argument("user-data-dir=./")
op.add_experimental_option("detach", True)
op.add_experimental_option("excludeSwitches", ["enable-logging"])


import json
from pathlib import Path

driver = uc.Chrome(chrome_options=op)
url = 'https://chat.openai.com'
url_login = 'https://chat.openai.com/auth/login/'

url_test = ""
uname = ""
passw = ""




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
    # Try to login with cookies
    load = False
    try:
        refresh(url_=url, wait_time_=4)
        driver.delete_all_cookies()
        load = load_cookie()
        if load:
            refresh(url_=url, wait_time_=4)
    except Exception as e:
        print("Error occurred when trying to login:", e)
    
    if not load:
        print("Need Log in")
        refresh(url_=url_login, wait_time_=8)
        inputElements = driver.find_elements(By.TAG_NAME, "button")
        inputElements[0].click()
        time.sleep(8)

        mail = driver.find_elements(By.TAG_NAME, "input")[1]
        mail.send_keys(MAIL)
        btn = driver.find_elements(By.TAG_NAME, "button")[0]
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
        wait = WebDriverWait(driver, 60)
        query = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
        query.send_keys(prompt)
        
        btnElements = driver.find_elements(By.TAG_NAME, "button")
        btnElements[-1].click()
        time.sleep(3)

    def get_output(): 
        output = "Unknown"
        kill_time = 0
        max_kill_time = 240
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
    
    prompt = filter_text(text=prompt)
    cls_n = "//div[@class='markdown prose w-full break-words dark:prose-invert light']"
    stop_generate_btn_class = "//button[@class='btn relative btn-neutral border-0 md:border']"

    send_input()
    while check_too_many_requests():
        time_out = random.randint(3, 7)
        message = "Waiting for " + str(time_out) + " minutes!!!"
        print(message)
        time.sleep(time_out*60)
        refresh(url_=url_test, wait_time_=3)
        send_input()
    print("Allowed to answer.")

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


def get_list_of_questions(input_path="./input/"):
    questions = []
    for i in range(len(os.listdir(input_path))):
        txt_file = "input_" + str(i) + ".txt"
        txt_file_path = os.path.join(input_path, txt_file)
        with open(txt_file_path, "r") as fi:
            cv = fi.read()
            questions.append(cv)
            fi.close()

    return questions


def run():
    openai_login(uname, passw)
    skip_popups()

    all_labels = ["Positive", "Negative", "Neutral", "Unknown"]
 
    result_list = []
    prefix = ""
    suffix = ". Show me that short extraction of this CV in json format and do not say anything else."
    
    questions = get_list_of_questions()

    for i, question in enumerate(questions):
        prompt = prefix + question + suffix
        
        try:
            response = get_response(prompt)
        except Exception as e:
            print("Error of this text", prompt)
            print("Error occurred when trying to request:", e)
            response = "{}"
            refresh(url_=url_test, wait_time_=4)
        
        json_object = json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
        json_file_path = "./output/output_" + str(i) + ".json"
        with open(json_file_path, "w") as fo:
            fo.write(json_object)
            fo.close()
    
    driver.close()


if __name__ == "__main__":
    run()