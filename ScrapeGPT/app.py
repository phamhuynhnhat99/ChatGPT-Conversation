import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import pickle
import pandas as pd
import random
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
# url_test = "https://chat.openai.com/chat/7dbecf1d-dc2b-41f4-9948-bc7a1cd53b8b"
url_test = ""
cookies_path = "cookies.json"

uname = "uname@example.com"
passw = "pass#example"


def bypassCloudfare():
    pass


def save_cookie():
    Path(cookies_path).write_text(
        json.dumps(driver.get_cookies(), indent=2)
    )
    print("Save success")


def load_cookie():
    load = False
    for cookie in json.loads(Path(cookies_path).read_text()):
        try:
            driver.add_cookie(cookie)
            load = True
        except:
            continue
    print("Load success")
    return load


def openai_login(MAIL, PASSWORD):
    # Try to log in with cookies
    try:
        driver.get(url)
        time.sleep(5)
        driver.delete_all_cookies()
        load = load_cookie()
        time.sleep(1)
        driver.get(url)
        time.sleep(4)
    except Exception as e:
        print("-----------> Loi o day ne", e)
    
    if not load:
        print("Need Log in")
        # Log in with account
        driver.get(url)
        time.sleep(10)
        inputElements = driver.find_elements(By.TAG_NAME, "button")
        inputElements[0].click()
        time.sleep(10)

        mail = driver.find_elements(By.TAG_NAME,"input")[1]
        mail.send_keys(MAIL)
        btn=driver.find_elements(By.TAG_NAME,"button")[0]
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
    driver.get(url_test)
    time.sleep(4)


def get_response(prompt):
    cls_n = "//div[@class='markdown prose w-full break-words dark:prose-invert light']"
    stop_generate_btn_class = "//button[@class='btn relative btn-neutral border-0 md:border']"

    inputElements = driver.find_elements(By.TAG_NAME, "textarea")
    inputElements[0].send_keys(prompt)
    driver.implicitly_wait(1)

    inputElements = driver.find_elements(By.TAG_NAME, "button")
    inputElements[-1].click()
    
    time.sleep(3)
    
    kill_time = 0
    max_kill_time = 200
    while kill_time < max_kill_time:
        btnText = driver.find_elements(By.XPATH, stop_generate_btn_class)
        if len(btnText) and btnText[0].text == "Regenerate response":
            kill_time = max_kill_time
        time.sleep(3)
        kill_time += 3

    time.sleep(3)
    outputElements = driver.find_elements(By.XPATH, cls_n)
    response = outputElements[-1].text

    return response


def get_list_of_comments(csv_path="test.csv"):
    df = pd.read_csv(csv_path)
    inds = range(0, 50, 1)
    short_cmt_df = df.iloc[inds]["content"]
    # short_cmt_df = df["content"]
    return list(short_cmt_df)

def run():
    openai_login(uname, passw)
    skip_popups()
 
    result_list = []
    test_list = get_list_of_comments()
    prefix = 'Phân tích '
    suffix = '. Chỉ được chọn "Thích", "Không thích", "Trung tính". Nếu không thể phân tích, trả lời "Không biết". Không được giải thích.'
    notice = 'Bắt đầu từ đây, Tôi sẽ yêu cầu bạn phân tích một câu bình luận trên Facebook, Bạn chỉ có thể trả lời "Thích", "Không thích" hoặc "Trung tính". Nếu không phân tích được, trả lời "Không biết". Không cần giải thích.'
    for i, cmt in enumerate(test_list):
        if i % 4 == 0:
            response = get_response(notice)
        prompt = prefix + '"' + cmt + '"' + suffix
        try:
            response = get_response(prompt)
        except:
            response = "Không biết"
        print(i)
        result_list.append(response)
        time.sleep(random.randint(6, 10))
    
    df = pd.DataFrame(result_list, columns=["Label"])
    df.to_csv("label.csv")
    driver.close()


if __name__ == "__main__":
    run()