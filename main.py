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

time.sleep(0.5)

driver.find_element(By.CSS_SELECTOR, "#email").send_keys(config.EMAIL) # 이메일 입력
driver.find_element(By.CSS_SELECTOR, "#pass").send_keys(config.PASSWORD) # 비밀번호 입력
driver.find_element(By.CSS_SELECTOR, "#loginbutton").click() # 로그인 버튼 클릭

time.sleep(0.5)
# 원래 창으로 전환(아래 오류 방지)
# urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(10054, '현재 연결은 원격 호스트에 의해 강제로 끊겼습니다', None, 10054, None))
try:
    driver.switch_to.window(original_window)
except NoSuchWindowException:
    pass

time.sleep(1)

driver.get(config.HOGANGNONO_MAIN_URL) # 메인 화면으로 이동을 통해 검색창 html 확보 셋팅
time.sleep(0.5)

driver.find_element(By.CLASS_NAME, "keyword").send_keys("반포동 반포자이", Keys.ENTER) # 특정 아파트 검색
time.sleep(0.5)

driver.find_elements(By.CLASS_NAME, "label-container")[0].click() # 특정 아파트 클릭
time.sleep(0.5)

driver.get(driver.current_url + "/2/review") # 특정 아파트의 후기 페이지로 이동
time.sleep(1)
html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

reviews = soup.select(".css-5k4zdz.scroll-content > .css-0")

for review in reviews:
    text_elements = review.select(".css-dei5sc > .css-9uvvzn > .css-1maot43.e1gnm0r1")

    for text_element in text_elements:
        text = text_element.get_text(strip=True)
        print(text)
        print()
