import os, sys
this_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_path)

from pathlib import Path
import time
import json
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

basic_url = 'https://chat.openai.com'
login_url = 'https://chat.openai.com/auth/login/'

class MyDriver:

    def __init__(self, name = "Unknown"):
        self.current_url = basic_url
        self.name = name
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = uc.Chrome(options=chrome_options)


    def turn_off(self):
        self.driver.quit()


    def go_to(self, url_=basic_url, wait_time_=4):
        self.driver.get(url_)
        time.sleep(wait_time_)


    def save_cookie(self, MAIL):
        cookies_subpath = "/Cookies/" + MAIL + ".json"
        cookies_path = this_path + cookies_subpath
        Path(cookies_path).write_text(
            json.dumps(self.driver.get_cookies(), indent=4)
        )
        print("Save success for", self.name)
        return cookies_subpath


    def load_cookie(self, cookies_subpath):
        load = False
        cookies_path = this_path + cookies_subpath
        cookies = json.loads(Path(cookies_path).read_text())
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
                load = True
            except:
                continue
        print("Load success for", self.name)
        return load
    

    def load_cookie(self, cookies_subpath):
        load = False
        cookies_path = this_path + cookies_subpath
        cookies = json.loads(Path(cookies_path).read_text())
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
                load = True
            except:
                continue
        print("Load success for", self.name)
        return load
    

    def openai_login(self, NAME, MAIL, PASSWORD, COOKIES):
        res_cookies = ""
        # Try to login with cookies
        load = False
        if len(COOKIES):
            try:
                self.go_to(url_=basic_url, wait_time_=4)
                self.driver.delete_all_cookies()
                load = self.load_cookie(COOKIES)
                if load:
                    self.go_to(url_=basic_url, wait_time_=1)
                    res_cookies = "Needless"
            except Exception as e:
                print(self.name, "Error occurred when trying to login with cookies:", e)
        
        if not load:
            print(NAME + "'s account needs to be logged in with a password.")
            self.go_to(url_=login_url, wait_time_=8)
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
            
            res_cookies = self.save_cookie(MAIL=MAIL)
        return res_cookies
    

    def skip_popups(self):
        xpath_0_1 = "//button[@class='btn relative btn-neutral ml-auto']"
        xpath_2 = "//button[@class='btn relative btn-primary ml-auto']"
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_0_1))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_0_1))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_2))).click()
        print(self.name, "Logging success!!!")
    

    def new_chat(self, prompt):
        def problems_existed():
            over = 0
            alert_class_name = "//div[@class='flex flex-grow flex-col gap-3']"
            alert = self.driver.find_elements(By.XPATH, alert_class_name)
            if len(alert):
                lastText = alert[-1].text
                _1st_alert = "Too many requests"
                _2nd_alert = "Something went wrong"
                _3rd_alert = "An error occurred"
                _4th_alert = "Network error"
                _5th_alert = "You've reached our limit"
                _6th_alert = "The conversation is too long, please start a new one"
                if _1st_alert in lastText or _2nd_alert in lastText or _3rd_alert in lastText or _4th_alert in lastText or _5th_alert in lastText:
                    over = 1
                elif _6th_alert in lastText:
                    over = 2
            return over

        def create_new_chat():
            wait = WebDriverWait(self.driver, 60)
            new_chat_btn = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
            new_chat_btn.click()

        def send_prompt():
            wait = WebDriverWait(self.driver, 120)
            query = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                )
            query.send_keys(prompt)
            btnElements = self.driver.find_elements(By.TAG_NAME, "button")
            btnElements[-1].click()

        def get_output():
            # Check Done Answering
            kill_time = 0
            max_kill_time = 200
            while kill_time < max_kill_time:
                stop_generate_btn_class = "//button[@class='btn relative btn-neutral -z-0 border-0 md:border']"
                btnText = self.driver.find_elements(By.XPATH, stop_generate_btn_class)
                if len(btnText) and btnText[0].text == "Regenerate response":
                    break
                time.sleep(2)
                kill_time += 2

            outputElements_class_name = "//div[@class='markdown prose w-full break-words dark:prose-invert light']"
            outputElements = self.driver.find_elements(By.XPATH, outputElements_class_name)
            output = outputElements[-1].text
            return output
        # ------------------------------------------------

        create_new_chat()
        send_prompt()
        print(self.name, ": Sent.")
        status = problems_existed()
        while status != 0:
            if status == 2:
                self.new_chat()
            time_out = random.randint(3, 5)
            message = self.name + ": Waiting for " + str(time_out) + " minutes!!!"
            print(message)
            time.sleep(time_out*60)
            self.go_to(url_=self.current_url, wait_time_=3)
            create_new_chat()
            send_prompt()
            status = self.problems_existed()
        print(self.name, ": Allowed to answer.")
        output = get_output()
        return output