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

#get more information about transactions
for _ in range(5):
    driver.find_element(By.CLASS_NAME, 'css-d8143a').click()

#find prices by XPATH
# Prices = driver.find_elements(By.XPATH, '//*[@id="scrollElement"]/div/div[5]/div/div[2]/div[3]/table/tbody')

# for Price in Prices:
#     print(Price.text)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
search_result = soup.select_one('.realPrice')

Price = search_result.select('.ebmi0c75')

for i in s:
    TEXT = i.get_text()
    print(TEXT)

#가격이 위치한곳이 Xpath
#//*[@id="scrollElement"]/div/div[5]/div/div[2]/div[3]/table/tbody/tr[23]/td[2]/div
#//*[@id="scrollElement"]/div/div[5]/div/div[2]/div[3]/table/tbody/tr[24]/td[2]/div
#//*[@id="scrollElement"]/div/div[5]/div/div[2]/div[3]/table/tbody/tr[35]/td[2]/div


