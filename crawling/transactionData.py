from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = Options()
options.add_experimental_option('detach', True)
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)

driver.get('https://hogangnono.com/')

#enter login page
driver.find_element(By.CLASS_NAME, 'css-wyfpkg').click()
driver.find_element(By.CLASS_NAME, 'btn-login').click()
driver.find_element(By.CLASS_NAME, 'css-13gnwd2').click()

#login with facebook account
driver.switch_to.window(driver.window_handles[1])
driver.find_element(By.ID, 'email').send_keys("1")
driver.find_element(By.ID, 'pass').send_keys("2")
driver.find_element(By.ID, 'loginbutton').click()

#find apartment
driver.switch_to.window(driver.window_handles[0])
driver.implicitly_wait(15)
driver.find_element(By.CLASS_NAME, 'css-1oc9vj8').click()
driver.find_element(By.CLASS_NAME, 'keyword').send_keys("헬리오시티")
driver.find_element(By.CLASS_NAME, 'btn-search').click()
driver.implicitly_wait(5)

#select first apartment
Aparts = driver.find_element(By.CLASS_NAME, 'apt').click() #Select Apartment
driver.implicitly_wait(5)

#get more information about transactions until year 5
while True:
    driver.find_element(By.CLASS_NAME, 'css-d8143a').click()
    driver.implicitly_wait(0.5)
    curdatahtml = driver.page_source

    cursoup = BeautifulSoup(curdatahtml, 'html.parser')
    cursearch_result = cursoup.select('.ebmi0c77')
    DateData = int(cursearch_result[-1].get_text().replace('.', ''))
    print(DateData)
    if (DateData<=230301): #get data until 230301
        break

#we have to put sleep because before click operation ends html parser start to crawl
driver.implicitly_wait(0.5)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
search_result = soup.select_one('.realPrice')

Date = search_result.select('.ebmi0c77')
Price = search_result.select('.ebmi0c75')
Floor = search_result.select('.ebmi0c73')

for A,B,C in zip(Date,Price,Floor):
    print("Date: {}, Floor: {}, Price: {}".format(A.get_text(),C.get_text(),B.get_text()))


