from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchWindowException, StaleElementReferenceException, NoSuchElementException
import time
import config
import json

import stop_words


def initialize_driver():
    user_agent = config.USER_AGENT

    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)


def login_hogangnono(driver):
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
    driver.get("https://hogangnono.com/apt/e694a/0/3/review")
    time.sleep(0.5)


def crawling_review(driver):
    review_list = []
    for i in range(10):
        try:  # 더보기 버튼이 있으면 클릭
            more_button = driver.find_element(By.CLASS_NAME, "css-wri049")
            more_button.click()
        except StaleElementReferenceException or NoSuchElementException:  # 더보기 버튼이 없으면 exception 발생. 따라서 스크롤 하도록 로직 구성
            element = driver.find_element(By.CSS_SELECTOR, ".css-5k4zdz.scroll-content > .css-0")
            driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(0.5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    reviews = soup.select(".css-5k4zdz.scroll-content > .css-0")  # 리뷰 전체를 가지고 있는 가장 큰 class
    for review in reviews:
        review_elements = review.select(".css-dei5sc > .css-9uvvzn > .css-1maot43.e1gnm0r1")  # 리뷰 text가 담긴 class
        for review_element in review_elements:
            review_text = review_element.get_text(strip=True)

            if not have_stop_word(review_text):
                review_list.append({"review": review_text})

    print(len(review_list))
    review_json = json.dumps(review_list, ensure_ascii=False, indent=4)
    print(review_json)


def have_stop_word(review_text):
    for stop_word in stop_words.dictionary:
        if stop_word in review_text:
            return True
    return False


if __name__ == "__main__":
    driver = initialize_driver()
    login_hogangnono(driver)
    crawling_review(driver)
