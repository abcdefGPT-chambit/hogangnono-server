from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time
from config import config, stop_words
import json
import re

like_text_pattern = r'(\d+)명'

def initialize_driver():
    user_agent = config.USER_AGENT

    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    options.add_argument('headless')
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
    driver.get("https://hogangnono.com/apt/qna9/0/2/review")
    time.sleep(0.5)


def crawling_review(driver):
    review_list = []
    like_list = []
    processing_list = []
    temp1_list = []
    temp2_list= []
    for i in range(20):
        try:  # 더보기 버튼이 있으면 클릭
            more_button = driver.find_element(By.CLASS_NAME, "css-wri049")
            more_button.click()
        except StaleElementReferenceException or NoSuchElementException:  # 더보기 버튼이 없으면 exception 발생. 따라서 스크롤 하도록 로직 구성
            element = driver.find_element(By.CSS_SELECTOR, ".css-5k4zdz.scroll-content > .css-0")
            driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    reviews = soup.select(".css-5k4zdz.scroll-content > .css-0")  # 리뷰 전체를 가지고 있는 가장 큰 class

    for review in reviews:
        review_elements = review.select(".css-dei5sc > .css-9uvvzn")  # 리뷰 text가 담긴 class
        like_elements = review.select(".css-dei5sc > .css-qvx8ct")
        # reply_elements = review.select(".css-19sk4h4 > .css-1901ou2 > .css-e3ehlk")

        for like_element in like_elements:
            like_text = like_element.get_text(strip=True)
            match_result = re.search(like_text_pattern, like_text)
            like_num = 0
            if match_result:
                like_num = int(match_result.group(1))
            like_list.append(like_num)

        for review_element in review_elements:
            review_text = review_element.get_text(strip=True)
            if "더보기" in review_text:
                review_text = review_text.replace("더보기", "")
            if not have_stop_word(review_text) and len(review_text) > 20: # 불용어를 가지고 있지 않고, 20자 이상인 경우
                review_list.append({"review": review_text})
                temp1_list.append(review_text)

        #print(f"불용어 처리 후 후기 수:{len(review_list)}")
        for i in range(len(review_list)):
            if like_list[i] > 10:
                processing_list.append(review_list[i])
                temp2_list.append(temp1_list[i])
        print(f"불용어 처리 + 일정 공감 수 이상 처리 후기 수:{len(processing_list)}")

        for temp in temp2_list:
            print(temp)
        # for reply_element in reply_elements:
        #     reply_text = reply_element.get_text(strip=True)
        # print(reply_text)

    json_review_list = json.dumps(processing_list, ensure_ascii=False, indent=4)
    #print(json_review_list)


def have_stop_word(review_text):
    for stop_word in stop_words.dictionary:
        if stop_word in review_text:
            return True
    return False


if __name__ == "__main__":
    driver = initialize_driver()
    login_hogangnono(driver)
    crawling_review(driver)