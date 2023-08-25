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