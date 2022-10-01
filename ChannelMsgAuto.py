import time
import re
from PyQt5.QtCore import QObject, pyqtSignal

from selenium import webdriver
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller
import os

from DBM import DBMgr
from Config import CONFIG
from BKLOG import DEBUG, INFO, ERROR


class ChannelMessageSending(QObject):
    running = pyqtSignal()
    finished = pyqtSignal()
    inserted = pyqtSignal(str)
    dupped = pyqtSignal(str, str)
    in_processing = pyqtSignal(int)
    one_processed = pyqtSignal(dict)
    need_msg = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.loop_flag = True

        self.setup_method()
        self.user_msgs = []

    def __del__(self):
        # INFO(f"채널 자동화 instance 삭제")
        self.teardown_method(None)

    def stop(self):
        self.loop_flag = False

    def get_chat_room(self, user):
        dbm = DBMgr.instance()

        sql = " \n".join((
            f"SELECT no, user_name, chat_room, reg_dtm",
            f"FROM user",
            f"WHERE",
            f"user_name = '{user}'",
        ))
        DEBUG(f"sql = [{sql}]")

        with dbm as conn:
            self.data = dbm.query(sql)

        DEBUG(f"data = [{self.data}]")

        if len(self.data) == 1:
            return self.data[0]["chat_room"]
        else:
            return user

    def setup_method(self):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # options.headless = True

        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        driver_path = f'./{chrome_ver}/chromedriver.exe'

        if os.path.exists(driver_path):
            INFO(f"chrom driver is insatlled: {driver_path}")
        else:
            INFO(f"install the chrome driver(ver: {chrome_ver})")
            chromedriver_autoinstaller.install(True)

        INFO(f"driver path = [{driver_path}]")

        self.driver = webdriver.Chrome(
            #executable_path="./driver/chromedriver.exe", options=options
            executable_path=driver_path, options=options
        )

        # if 'browserVersion' in self.driver.capabilities:
        #     INFO(f"chrome browserVersion: [{self.driver.capabilities['browserVersion']}]")
        # else:
        #     INFO(f"chrome Version: [{self.driver.capabilities['version']}]")


        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    # def sendMessage(self):
    def run(self):
        self.running.emit()
        # 1 | open | / |
        self.driver.get("https://center-pf.kakao.com/")
        # 2 | setWindowSize | 517x770 |
        self.driver.set_window_size(567, 770)

        ## 로그인 분기처리
        # accounts.kakao.com/login
        DEBUG(f"url = [{self.driver.current_url}]")

        dashboard_pattern = re.compile(r"^https://business.kakao.com/dashboard")
        login_pattern = re.compile(r"^https://accounts.kakao.com/login")

        if login_pattern.match(self.driver.current_url):
            # 로그인 처리 필요
            INFO(f"로그인 필요!!")
            try:
                # 4 | type | id=id_email_2 |
                #self.driver.find_element(
                #    By.XPATH, "//input[@id='id_email_2']"
                #).send_keys(CONFIG["channel_login"]["user_id"])
                #self.driver.find_element(
                #    By.ID, "input-loginKey"
                #).send_keys(CONFIG["channel_login"]["user_id"])
                self.driver.find_element(
                    By.NAME, "email"
                ).send_keys(CONFIG["channel_login"]["user_id"])
                # 7 | type | id=id_password_3 |
                #self.driver.find_element(
                #    By.XPATH, "//input[@id='id_password_3']"
                #).send_keys(CONFIG["channel_login"]["user_pw"])
                #self.driver.find_element(
                #    By.ID, "input-password"
                #).send_keys(CONFIG["channel_login"]["user_pw"])
                self.driver.find_element(
                    By.NAME, "password"
                ).send_keys(CONFIG["channel_login"]["user_pw"])
                # 6 | sendKeys | id=id_password_3 | ${KEY_ENTER}
                #self.driver.find_element(
                #    By.XPATH, "//input[@id='id_password_3']"
                #).send_keys(Keys.ENTER)
                #self.driver.find_element(
                #    By.ID, "input-password"
                #).send_keys(Keys.ENTER)
                self.driver.find_element(
                    By.NAME, "password"
                ).send_keys(Keys.ENTER)
            except selenium.common.exceptions.ElementClickInterceptedException as ecie:
                DEBUG(f"skip login error, have to login manually [{ecie}]")

            while True:
                if dashboard_pattern.match(self.driver.current_url):
                    # 로그인 되었음
                    # time.sleep(1)
                    break

                INFO(f"로그인 대기!!")
                time.sleep(5)

            INFO(f"대쉬보드로 이동")
            # not clickable error fix but solved by script click
            #self.driver.maximize_window()
            # 20211227 변경
            # element = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located(
            #         (
            #             By.XPATH,
            #             "//a[contains(@href, 'https://center-pf.kakao.com/_RdKNT/dashboard')]",
            #         )
            #     )
            # )
            # element.click()
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        #By.XPATH,
                        #"//span[contains(.,\'리드101송도학원\')]",
                        By.CSS_SELECTOR,
                        ".name_profile",
                    )
                )
            )
            #element.click()
            self.driver.execute_script("arguments[0].click();", element)
 
            #self.driver.find_element(By.CSS_SELECTOR, ".name_profile").click()
            #time.sleep(5)
            #self.driver.find_element(By.XPATH, "//div/a/span").click()
            #self.driver.find_element(By.CSS_SELECTOR, ".name_profile").click()
            INFO(f"대쉬보드로 이동 click")

        # 20211227 변경
        elif dashboard_pattern.match(self.driver.current_url):
            # 이미 로그인 되어 있음
            # 3 | click | css=.tit_invite |
            #self.driver.find_element(By.CSS_SELECTOR, ".tit_invite").click()
            self.driver.find_element(By.CSS_SELECTOR, ".name_profile").click()
        else:
             # 3 | click | css=.tit_invite |
            #self.driver.find_element(By.CSS_SELECTOR, ".tit_invite").click()
            self.driver.find_element(By.CSS_SELECTOR, ".name_profile").click()


        # if dashboard_pattern.match(self.driver.current_url):
        #     # 이미 로그인 되어 있음
        #     # 3 | click | css=.tit_invite |
        #     element = WebDriverWait(self.driver, 10).until(
        #         EC.presence_of_element_located(
        #             (
        #                 By.CSS_SELECTOR,
        #                 ".cont_thumb",
        #             )
        #         )
        #     )
        #     element.click()
    
        # else:
        #     # 3 | click | css=.tit_invite |
        #     element = WebDriverWait(self.driver, 10).until(
        #         EC.presence_of_element_located(
        #             (
        #                 By.CSS_SELECTOR,
        #                 ".cont_thumb",
        #             )
        #         )
        #     )
        #     element.click()
 
        # 4 | click | xpath=//div[@id='mFeature']/div/div[2]/ul/li[3]/a |
        #self.driver.find_element(
        #    By.XPATH, "//div[@id='mFeature']/div/div[2]/ul/li[3]/a"
        #).click()
        #20211108 변경되었음
        INFO(f"1:1채팅")
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@id=\'mFeature\']/div/div[2]/ul/li[3]/a",
                )
            )
        )
        #element.click()
        self.driver.execute_script("arguments[0].click();", element)
        INFO(f"1:1채팅 클릭!!")

        #INFO(f"채팅 메뉴 로딩 대기!!")
        #time.sleep(5)

        # 5 | click | linkText=채팅 목록 |
        INFO(f"채팅목록")
        #self.driver.find_element(By.LINK_TEXT, "채팅 목록").click()
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.LINK_TEXT,
                    "채팅 목록",
                )
            )
        )
        self.driver.execute_script("arguments[0].click();", element)

        while self.loop_flag:
            self.running.emit()
            # msgList에서 발송 대상자를 가져온다.
            self.need_msg.emit()
            time.sleep(1)
            for user_msg in self.user_msgs:
                try:
                    chat_room = self.get_chat_room(user_msg["user"])
                    INFO(f"chat_room = [{chat_room}]")
                    if CONFIG["RUN_MODE"] != "REAL":
                        chat_room = "시은아빠"
                    # 6 | click | name=keyword |
                    element = self.driver.find_element(By.NAME, "keyword")
                    actions = ActionChains(self.driver)
                    actions.double_click(element).perform()

                    # 7 | type | name=keyword |
                    self.driver.find_element(By.NAME, "keyword").clear()
                    self.driver.find_element(By.NAME, "keyword").send_keys(chat_room)
                    # 9 | sendKeys | name=keyword | ${KEY_ENTER}
                    self.driver.find_element(By.NAME, "keyword").send_keys(Keys.ENTER)
                    # 10 | click | css=.txt_info:nth-child(1) |
                    self.vars["window_handles"] = self.driver.window_handles

                    time.sleep(1)
                    # 11 | storeWindowHandle | root |
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
                    msg_list = user_msg["message"].split(sep="\n")
                    for i, message in enumerate(msg_list):
                        self.driver.find_element(By.ID, "chatWrite").send_keys(message)
                        if i != len(msg_list) - 1:
                            self.driver.find_element(By.ID, "chatWrite").send_keys(
                                Keys.SHIFT + Keys.ENTER
                            )
                    self.driver.find_element(By.ID, "chatWrite").send_keys(Keys.ENTER)
                    time.sleep(1)
                    # 17 | selectWindow | handle=${root} |
                    # 18 | click | name=keyword |
                    self.driver.close()
                    # 19 | click | css=.box_tf |
                    self.driver.switch_to.window(self.vars["root"])

                    self.one_processed.emit(user_msg)

                except selenium.common.exceptions.TimeoutException as te:
                    ERROR(f"[{user_msg}] 메시지 전송에 실패하였습니다. [{te}]")
                finally:
                    del self.user_msgs[0]

        self.teardown_method(None)


if __name__ == "__main__":
    DEBUG(f"CONFIG[user_id]=[{CONFIG['channel_login']['user_id']}]")
    DEBUG(f"CONFIG[user_pw]=[{CONFIG['channel_login']['user_pw']}]")
    # DEBUG(f"CONFIG=[{CONFIG}]")
    user = {
        "name": "시은아빠",
        "message": "테스트 입니다.",
    }

    w = ChannelMessageSending(user)
    w.sendMessage()
