import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time

@st.cache_data
def crawl_search():
    browser = webdriver.Chrome()
    browser.get("https://ma-pia.net/keyword/keyword.php")
    time.sleep(2)

    today_close = browser.find_elements("css selector", "a#closeToday")[0]
    today_close.click()
    time.sleep(1)

    keyword = ['하이퍼클로바X', '네이버 하이퍼클로바X', '클로바X', '네이버 클로바X', '네이버 큐', '네이버 CUE']

    input_text = browser.find_elements("css selector", "textarea#DataQ1")[0]
    input_text.clear()

    for word in keyword:
        input_text.send_keys(word)
        input_text.send_keys(Keys.RETURN)

    search_btn = browser.find_elements("css selector", "button#SDsave")[0]
    search_btn.click()
    time.sleep(3)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    tr = soup.select("tbody.sch_tbody > tr")

    cue = int(tr[0]['data-totalsum'].replace(",", '')) + int(tr[1]['data-totalsum'].replace(",", ''))
    cloverX = int(tr[2]['data-totalsum'].replace(",", '')) + int(tr[3]['data-totalsum'].replace(",", ''))
    hypercloverX = int(tr[4]['data-totalsum'].replace(",", '')) + int(tr[5]['data-totalsum'].replace(",", ''))

    browser.quit()

    return cue, cloverX, hypercloverX