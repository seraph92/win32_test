# Generated by Selenium IDE
# import pytest
import time
import json
import re

from selenium import webdriver
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

from Config import CONFIG


class ChannelMessageSending:
    def __init__(self, user):
        self.setup_method()
        self.users = []
        self.users.append(user)

    def setup_method(self):
        options = Options()
        # options.headless = True

        self.driver = webdriver.Chrome(
            executable_path="./driver/chromedriver.exe", options=options
        )
        # self.driver = webdriver.Chrome()

        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def sendMessage(self):
        # Test name: 메시지 발송 테스트2
        # Step # | name | target | value
        # 1 | open | / |
        self.driver.get("https://center-pf.kakao.com/")
        # 2 | setWindowSize | 517x770 |
        self.driver.set_window_size(567, 770)

        ## 로그인 분기처리
        # accounts.kakao.com/login
        print(f"url = [{self.driver.current_url}]")

        dashboard_pattern = re.compile(r"^https://business.kakao.com/dashboard")

        login_pattern = re.compile(r"^https://accounts.kakao.com/login")

        if login_pattern.match(self.driver.current_url):
            # 로그인 처리 필요
            print(f"로그인 필요!!")
            try:
                # 3 | click | id=id_email_2 |
                # self.driver.find_element(By.XPATH, "//input[@id='id_email_2']").click()
                # 4 | type | id=id_email_2 |
                self.driver.find_element(
                    By.XPATH, "//input[@id='id_email_2']"
                ).send_keys(CONFIG["user_id"])
                # 5 | click | id=id_password_3 |
                # self.driver.find_element(By.XPATH, "//input[@id='id_password_3']").click()
                # 7 | type | id=id_password_3 |
                self.driver.find_element(
                    By.XPATH, "//input[@id='id_password_3']"
                ).send_keys(CONFIG["user_pw"])
                # 6 | sendKeys | id=id_password_3 | ${KEY_ENTER}
                self.driver.find_element(
                    By.XPATH, "//input[@id='id_password_3']"
                ).send_keys(Keys.ENTER)
            except selenium.common.exceptions.ElementClickInterceptedException as ecie:
                print(f"skip login error, have to login manually [{ecie}]")

            while True:
                if dashboard_pattern.match(self.driver.current_url):
                    # 로그인 되었음
                    # time.sleep(1)
                    break

                time.sleep(5)

            # click | css=.link_title |
            # time.sleep(1)
            # self.driver.find_element(By.CSS_SELECTOR, ".link_title").click()
            self.driver.find_element(
                By.XPATH,
                "//a[contains(@href, 'https://center-pf.kakao.com/_RdKNT/dashboard')]",
            ).click()

        elif dashboard_pattern.match(self.driver.current_url):
            # 이미 로그인 되어 있음
            # 3 | click | css=.tit_invite |
            self.driver.find_element(By.CSS_SELECTOR, ".tit_invite").click()
            # 3 | click | css=.tit_invite |
            # self.driver.find_element(By.CSS_SELECTOR, ".tit_invite").click()
            # self.driver.find_element(By.XPATH, "//strong[contains(.,\'리드101송도학원\')]").click()
        else:
            # 3 | click | css=.tit_invite |
            self.driver.find_element(By.CSS_SELECTOR, ".tit_invite").click()

        # if title:
        #   ## 로그인 되어 있음
        #   print(f"로그인 되어 있음!!")
        # else:
        #   ## 로그인 해야 함
        #   print(f"로그인 해야함")

        # self.driver.close()

        # 4 | click | xpath=//div[@id='mFeature']/div/div[2]/ul/li[3]/a |
        self.driver.find_element(
            By.XPATH, "//div[@id='mFeature']/div/div[2]/ul/li[3]/a"
        ).click()
        # 5 | click | linkText=채팅 목록 |
        self.driver.find_element(By.LINK_TEXT, "채팅 목록").click()

        while True:
            for user in self.users:
                time.sleep(5)
                # 6 | click | name=keyword |
                # self.driver.find_element(By.NAME, "keyword").click()
                # self.driver.find_element(By.NAME, "keyword").click()
                element = self.driver.find_element(By.NAME, "keyword")
                actions = ActionChains(self.driver)
                actions.double_click(element).perform()

                # 7 | type | name=keyword |
                self.driver.find_element(By.NAME, "keyword").send_keys(user["name"])
                # 8 | type | name=keyword |
                # self.driver.find_element(By.NAME, "keyword").send_keys(user['name'])
                # 9 | sendKeys | name=keyword | ${KEY_ENTER}
                self.driver.find_element(By.NAME, "keyword").send_keys(Keys.ENTER)
                # 10 | click | css=.txt_info:nth-child(1) |
                self.vars["window_handles"] = self.driver.window_handles

                time.sleep(1)
                # 11 | storeWindowHandle | root |
                # self.driver.find_element(By.CSS_SELECTOR, ".txt_info:nth-child(1)").click()
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".txt_info:nth-child(1)")
                    )
                )
                element.click()
                # 12 | selectWindow | handle=${win1697} |
                self.vars["win1697"] = self.wait_for_window(2000)
                # 13 | click | id=chatWrite |
                self.vars["root"] = self.driver.current_window_handle
                # 14 | type | id=chatWrite | abc
                self.driver.switch_to.window(self.vars["win1697"])
                # 15 | click | css=.btn_g |
                self.driver.find_element(By.ID, "chatWrite").click()
                # 16 | close |  |
                self.driver.find_element(By.ID, "chatWrite").send_keys(user["message"])
                self.driver.find_element(By.ID, "chatWrite").send_keys(Keys.ENTER)
                time.sleep(1)
                # 17 | selectWindow | handle=${root} |
                # self.driver.find_element(By.CSS_SELECTOR, ".btn_g").click()
                # 18 | click | name=keyword |
                self.driver.close()
                # 19 | click | css=.box_tf |
                self.driver.switch_to.window(self.vars["root"])

            # # 20 | type | name=keyword | 이시은
            # self.driver.find_element(By.NAME, "keyword").click()
            # # 21 | sendKeys | name=keyword | ${KEY_ENTER}
            # self.driver.find_element(By.CSS_SELECTOR, ".box_tf").click()
            # # 22 | click | css=.txt_info:nth-child(1) |
            # self.driver.find_element(By.NAME, "keyword").send_keys("이시은")
            # # 23 | selectWindow | handle=${win4320} |
            # self.driver.find_element(By.NAME, "keyword").send_keys(Keys.ENTER)
            # # 24 | click | id=chatWrite |
            # self.vars["window_handles"] = self.driver.window_handles
            # # 25 | type | id=chatWrite | test
            # self.driver.find_element(By.CSS_SELECTOR, ".txt_info:nth-child(1)").click()
            # # 26 | click | css=.btn_g |
            # self.vars["win4320"] = self.wait_for_window(2000)
            # # 27 | close |  |
            # self.driver.switch_to.window(self.vars["win4320"])
            # # 28 | selectWindow | handle=${root} |
            # self.driver.find_element(By.ID, "chatWrite").click()
            # # 29 | close |  |
            # self.driver.find_element(By.ID, "chatWrite").send_keys("test")
            # self.driver.find_element(By.CSS_SELECTOR, ".btn_g").click()
            # self.driver.close()
            # self.driver.switch_to.window(self.vars["root"])

            # 10초간 sleep
            time.sleep(10)

        self.driver.close()


if __name__ == "__main__":
    print(f"CONFIG[user_id]=[{CONFIG['user_id']}]")
    print(f"CONFIG[user_pw]=[{CONFIG['user_pw']}]")
    # print(f"CONFIG=[{CONFIG}]")
    user = {
        "name": "이범각",
        "message": "테스트 입니다.",
    }

    w = ChannelMessageSending(user)
    w.sendMessage()

    # pattern = re.compile(
    #   r"^https://business.kakao.com/dashboard"
    # )

    # if pattern.match("https://accounts.kakao.com/login/kakaobusiness?continue=https://business.kakao.com/dashboard/?sid%3Dpfr"):
    #   print(f"포함되어 있어")
    # else:
    #   print(f"포함되어 있지 않아")
