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

import json
from pathlib import Path

url = 'https://chat.openai.com'
url_login = 'https://chat.openai.com/auth/login/'

op = webdriver.ChromeOptions()
op.add_argument('--headless=new')
op.add_argument(f"user-agent={UserAgent.random}")
op.add_argument("user-data-dir=./")
op.add_experimental_option("detach", True)
op.add_experimental_option("excludeSwitches", ["enable-logging"])



url_current = ""

uname = ""
passw = ""

class MyDriver:

    def __init__(self):
        self.driver = uc.Chrome(chrome_options=op)
        self.cookies_path = "cookies.json"
        self.prefix_0 = 'Trong một livestream bán mặc hàng '
        self.prefix_1 = '. Hãy phân tích bình luận sau "'
        
        self.suffix_1 = '". Nếu nhắc tên riêng hoặc muốn chia sẻ thì đáp án là 1.'
        self.suffix_2 = ' Nếu đang thắc mắc thì đáp án là 2.'
        self.suffix_3 = ' Nếu muốn chọn thông số cho sản phẩm thì đáp án là 3.'
        self.suffix_4 = ' Nếu đã chốt đơn nhưng chưa nhận được sản phẩm thì đáp án là 4.'
        self.suffix_5 = ' Nếu đã nhận được sản phẩm và không thích sản phẩm thì đáp án là 5.'
        self.suffix_6 = ' Nếu đã nhận được sản phẩm và thích sản phẩm thì đáp án là 6.'
        self.suffix_7 = ' Nếu người bình luận muốn hủy đơn hàng hoặc không muốn nhận sản phẩm thì đáp án là 7.'
        self.suffix_0 = ' Chọn 1 trong các nhãn trên. Các trường hợp khác hoặc không phân tích được thì đáp án là 0. Trả lời theo format: Đáp án. Giải thích ngắn.'


    def close(self):
        self.driver.close()


    def go_to(self, url_=url, wait_time_=4):
        self.driver.get(url_)
        time.sleep(wait_time_)

    
    def save_cookie(self):
        Path(self.cookies_path).write_text(
            json.dumps(self.driver.get_cookies(), indent=4)
        )
        print("Save success")


    def load_cookie(self):
        load = False
        cookies = json.loads(Path(self.cookies_path).read_text())
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
                load = True
            except:
                continue
        print("Load success")
        return load
    

    def openai_login(self, MAIL=uname, PASSWORD=passw):
        # Try to login with cookies
        load = False
        try:
            self.go_to(url_=url, wait_time_=4)
            self.driver.delete_all_cookies()
            load = self.load_cookie()
            if load:
                self.go_to(url_=url, wait_time_=1)
        except Exception as e:
            print("Error occurred when trying to login:", e)
        
        if not load:
            print("Need Log in")
            self.go_to(url_=url_login, wait_time_=8)
            inputElements = self.driver.find_elements(By.TAG_NAME, "button")
            inputElements[0].click()
            time.sleep(8)

            mail = self.driver.find_elements(By.TAG_NAME, "input")[1]
            mail.send_keys(MAIL)
            btn = self.driver.find_elements(By.TAG_NAME, "button")[0]
            btn.click()

            password = self.driver.find_elements(By.TAG_NAME,"input")[2]
            password.send_keys(PASSWORD)
            btn = self.driver.find_elements(By.TAG_NAME,"button")[1]
            btn.click()
            
            # time.sleep(3)
            self.save_cookie()


    def skip_popups(self):
        xpath_0_1 = "//button[@class='btn relative btn-neutral ml-auto']"
        xpath_2 = "//button[@class='btn relative btn-primary ml-auto']"
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_0_1))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_0_1))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_2))).click()
        print("Logging success!!!")
        self.go_to(url_=url_current, wait_time_=2)


    def new_chat(self):
        wait = WebDriverWait(self.driver, 60)
        new_chat_btn = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
        new_chat_btn.click()
        wait = WebDriverWait(self.driver, 120)
        query = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
        query.send_keys("Hi there")
        btnElements = self.driver.find_elements(By.TAG_NAME, "button")
        btnElements[-1].click()
        self.go_to(url_=url, wait_time_=3)
        
        new_chat_wait = WebDriverWait(self.driver, 10)
        new_chat_cln = "//div[@class='flex-1 text-ellipsis max-h-5 overflow-hidden break-all relative']"
        new_chat_wait.until(EC.element_to_be_clickable((By.XPATH, new_chat_cln)))
        new_chat = self.driver.find_elements(By.XPATH, new_chat_cln)[0]
        new_chat.click()
        self.driver.implicitly_wait(2)
        url_current = self.driver.current_url


    def get_answer(self, input_file):
        def filter_text(text):
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
            return emoji_pattern.sub(r'', text)
        
        def problems_existed():
            over = 0
            cls_n = "//div[@class='flex flex-grow flex-col gap-3']"
            many_requests_alert = self.driver.find_elements(By.XPATH, cls_n)
            if len(many_requests_alert):
                lastText = many_requests_alert[-1].text
                _1st_alert = "Too many requests in 1 hour."
                _2nd_alert = "Something went wrong."
                _3rd_alert = "An error occurred."
                _4th_alert = "The conversation is too long, please start a new one."
                if _1st_alert in lastText or _2nd_alert in lastText or _3rd_alert in lastText:
                    over = 1
                elif _4th_alert in lastText:
                    over = 2
            return over

        def send_input(prompt):
            wait = WebDriverWait(self.driver, 120)
            query = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                )
            query.send_keys(prompt)
            btnElements = self.driver.find_elements(By.TAG_NAME, "button")
            btnElements[-1].click()
            time.sleep(1)

        def get_output(): 

            def filter_output(text):
                res = 0
                try:
                    ind = [99, 99, 99, 99, 99, 99, 99, 99]
                    for i in range(7+1):
                        j = str(i)
                        if j in text:
                            ind[i] = text.index(j)
                    res = ind.index(min(ind))
                except Exception:
                    res = 0
                return str(res)

            cls_n = "//div[@class='markdown prose w-full break-words dark:prose-invert light']"
            outputElements = self.driver.find_elements(By.XPATH, cls_n)
            output = outputElements[-1].text
            return output, filter_output(output)
        
        def filter_csv(input_file):
            df = pd.read_csv(input_file, dtype=str, keep_default_na=False)
            # Pre-processing
            labels = list(df.label.unique())
            selected_labels = []
            for label in labels:
                tmp = df[df["label"] == label]
                if len(tmp) > 20:
                    selected_labels.append(label)
            df = df.loc[df["label"].isin(selected_labels)]
            int_label = [int(float(_)) for _ in df.label]
            df["label"] = int_label
            return df
        
        df = filter_csv(input_file).iloc[50000:123000]
        contents = list(df["comment"])
        categories = list(df["category"])
        y_true = list(df["label"])
        y_pred = []
        y_text = []

        self.suffix = self.suffix_1 + self.suffix_2 + self.suffix_3 + self.suffix_4 + self.suffix_5 + self.suffix_6 + self.suffix_7 + self.suffix_0
        i_cache = 0
        num_samples_each_file = 100
        for i, text_category in enumerate(zip(contents, categories)):
            if i >= 500:
                text, category = text_category
                # content = filter_text(text).replace("\n", " ")
                prompt = self.prefix_0 + category + self.prefix_1 + text + self.suffix
                try:
                    send_input(prompt)
                    status = problems_existed()
                    while status != 0:
                        if status == 2:
                            self.new_chat()
                        time_out = random.randint(3, 5)
                        message = "Waiting for " + str(time_out) + " minutes!!!"
                        print(message)
                        time.sleep(time_out*60)
                        self.go_to(url_=url_current, wait_time_=3)
                        send_input(prompt)
                        status = problems_existed()
                    print("Allowed to answer.")

                    kill_time = 0
                    max_kill_time = 200
                    while kill_time < max_kill_time:
                        stop_generate_btn_class = "//button[@class='btn relative btn-neutral border-0 md:border']"
                        btnText = self.driver.find_elements(By.XPATH, stop_generate_btn_class)
                        if len(btnText) and btnText[0].text == "Regenerate response":
                            break
                        time.sleep(3)
                        kill_time += 3

                    response, gpt_label = get_output()
                except Exception as e:
                    print("Error of this text", prompt)
                    print("Error occurred when trying to request:", e)
                    response = "Error occurred"
                    gpt_label = "0"
                    self.go_to(url_=url_current, wait_time_=4)
                
                y_pred.append(gpt_label)
                y_text.append(response)

                try:
                    if len(y_pred)==num_samples_each_file:
                        ans_df = pd.DataFrame()
                        ans_df["y_true"] = y_true[i_cache:i_cache+len(y_pred)]
                        ans_df["y_pred"] = y_pred
                        ans_df["y_text"] = y_text
                        ans_df["content"] = contents[i_cache:i_cache+len(y_pred)]
                        ans_df["category"] = categories[i_cache:i_cache+len(y_pred)]
                        
                        name = "/home/aia/Nhat/ChatGPT-Conversation/Sales_LocalAPI/gpt/predict_" + str(i//num_samples_each_file) + ".csv"
                        ans_df.to_csv(name, index=False)
                        print("predict_" + str(i//num_samples_each_file) + " have done.")
                        y_pred = []
                        y_text = []
                        i_cache = i+1
                except Exception as e:
                    print(e)
        
        if len(y_pred) > 0:
            ans_df = pd.DataFrame()
            ans_df["y_true"] = y_true[i_cache:i_cache+len(y_pred)]
            ans_df["y_pred"] = y_pred
            ans_df["y_text"] = y_text
            ans_df["content"] = contents[i_cache:i_cache+len(y_pred)]
            ans_df["category"] = categories[i_cache:i_cache+len(y_pred)]
            name = "/home/aia/Nhat/ChatGPT-Conversation/Sales_LocalAPI/gpt/predict_xxx.csv"
            ans_df.to_csv(name, index=False)
            print("predict_xxx have done.")

        # return txt_to_json(response.replace("\n", " "))
        # return '{"message": "Well done"}'
        
    
def txt_to_json(text):
    ans = '{"message": "not enough"}'
    try:
        i = text.index('{')
        j = len(text) - text[::-1].index('}') - 1
        ans = text[i:j+1]
    except Exception as e:
        ans = '{"message": "not enough"}'
    return ans