from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchWindowException
import time
import config

user_agent = config.USER_AGENT

options = Options()
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

driver.get(config.HOGANGNONO_MAIN_URL)
time.sleep(0.5)

driver.find_element(By.CSS_SELECTOR, ".css-wyfpkg").click() # SMS 설치 팝업창 닫기
time.sleep(0.5)

driver.find_element(By.CSS_SELECTOR, ".btn-login").click() # 우측 상단 로그인 버튼 클릭
time.sleep(0.5)

driver.find_element(By.CSS_SELECTOR, ".css-0").click() # 페이스북 로그인 버튼 클릭
time.sleep(1)

original_window = driver.window_handles[0] # 메인 창 저장

# 페이스북 로그인 창으로 전환
for window_handle in driver.window_handles:
    driver.switch_to.window(window_handle)
    if "Facebook" in driver.title:
        break

driver.find_element(By.CSS_SELECTOR, "#email").send_keys(config.EMAIL) # 이메일 입력
