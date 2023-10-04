from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time
from config import config


def initialize_driver():
    user_agent = config.USER_AGENT

    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Headless 모드 활성화
    options.add_experimental_option("detach", True)

    # permissions - policy: interest - cohort = ()

    return webdriver.Chrome(options=options)


def scroll_to_bottom(driver):
    # 페이지 하단으로 스크롤
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def crawling_review(driver, url):
    driver.get(config.HOGANGNONO_MAIN_URL)
    driver.find_element(By.CSS_SELECTOR, ".css-wyfpkg").click()  # SMS 설치 팝업창 닫기
    driver.find_element(By.CSS_SELECTOR, ".btn-login").click()  # 우측 상단 로그인 버튼 클릭
    driver.find_element(By.CSS_SELECTOR, ".css-d7mu49").click()  # 페이스북 로그인 버튼 클릭
    original_window = driver.window_handles[0]  # 메인 창 저장

    # 페이스북 로그인 창으로 전환
    for window_handle in driver.window_handles:
        driver.switch_to.window(window_handle)
        if "Facebook" in driver.title:
            break

    driver.find_element(By.CSS_SELECTOR, "#email").send_keys(config.EMAIL)  # 이메일 입력
    driver.find_element(By.CSS_SELECTOR, "#pass").send_keys(config.PASSWORD)  # 비밀번호 입력
    driver.find_element(By.CSS_SELECTOR, "#loginbutton").click()  # 로그인 버튼 클릭

    driver.switch_to.window(original_window)
    time.sleep(4)
    # driver.get(config.HOGANGNONO_MAIN_URL)
    driver.get(url)
    time.sleep(0.5)

    review_list = []

    for i in range(1):
        try:  # 더보기 버튼이 있으면 클릭
            more_button = driver.find_element(By.CLASS_NAME, "css-wri049")
            more_button.click()
        except StaleElementReferenceException or NoSuchElementException:  # 더보기 버튼이 없으면 exception 발생. 따라서 스크롤 하도록 로직 구성
            element = driver.find_element(By.CSS_SELECTOR, ".css-5k4zdz.scroll-content > .css-0")
            driver.execute_script("arguments[0].scrollIntoView();", element)

        time.sleep(0.5)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    reviews = soup.select(".css-5k4zdz.scroll-content > .css-0")

    for review in reviews:
        text_elements = review.select(".css-dei5sc > .css-9uvvzn > .css-1maot43.e1gnm0r1")

        for text_element in text_elements:
            text = text_element.get_text(strip=True)
            review_list.append({"review": text})

    print(review_list)

    return review_list
