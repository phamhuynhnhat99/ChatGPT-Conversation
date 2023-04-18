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

def run():
    openai_login(uname, passw)
    
    driver.close()


if __name__ == "__main__":
    run()