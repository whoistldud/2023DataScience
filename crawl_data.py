import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd

# 데이터 파일 불러오는 함수
def open_data(val):
    try:
        ex_data = pd.read_excel(f"./project_data{val}.xlsx")
    except FileNotFoundError:
        # 파일이 없는 경우 새로운 DataFrame 생성
        ex_data = pd.DataFrame(coloumns=['new','제목', '언론사', '최종입력시간', '입력시간', 'URL', '본문'])
    return ex_data
    
# 크롤링 하는 함수
@st.cache_data
def crawl_data(word, crawl_start, today):

    word = "네이버 "+word
    news_data = []
    # 크롤링 기간 설정 (크롤링 시작 날짜 정하는 로직 main에서 짜야함)
    crowl_url = f"https://search.naver.com/search.naver?where=news&query={word}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={crawl_start}&de={today}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom20231105to20231105&is_sug_officeid=0&office_category=0&service_area=0"

    # 브라우저 열기 & 웹페이지 접속
    browser = webdriver.Chrome()
    browser.get(crowl_url)
    time.sleep(2)

    soup = BeautifulSoup(browser.page_source, "html.parser")

    # 크롤링해야 하는 기사 링크 담아놓을 리스트
    news_link = []

    # ainfo = 결과 기사의 언론사, '네이버뉴스' 태그 리스트
    ainfo = browser.find_elements("css selector", "ul.list_news li.bx div.info_group a.info")
    
    
    # 네이버뉴스 달려있는 기사링크만 추출!
    for i,a in enumerate(ainfo):
        if a.text == '네이버뉴스':
            link = soup.select("div.info_group a.info")[i]['href']
            news_link.append(link)


    # 다음 페이지 버튼이 활성화되어 있는 경우
    # = 다음 페이지가 존재하는 경우
    # = is_next_page 값이 'false'인 경우
    is_next_page = soup.select("a.btn_next")[0]['aria-disabled']
    btn_next = browser.find_elements("css selector", "a.btn_next")[0]

    while True:

        if is_next_page == 'false':
            btn_next.click()
            time.sleep(1)

            ainfo = browser.find_elements("css selector", "ul.list_news li.bx div.info_group a.info")
            soup = BeautifulSoup(browser.page_source, "html.parser")
            for i,a in enumerate(ainfo):
                if a.text == '네이버뉴스':
                    link = soup.select("div.info_group a.info")[i]['href']
                    news_link.append(link)

            is_next_page = soup.select("a.btn_next")[0]['aria-disabled']
            btn_next = browser.find_elements("css selector", "a.btn_next")[0]

        elif is_next_page == 'true':
            break
        else:
            break

    if len(news_link) == 0:
        return []

    # 링크 하나씩 넣어서 크롤링 시작
    for news in news_link:
        browser.get(news)
        time.sleep(1)

        # 기사 제목
        title = browser.find_elements("css selector", "h2#title_area")[0].text

        # 언론사
        soup = BeautifulSoup(browser.page_source, "html.parser")
        company = soup.select("a.media_end_head_top_logo._LAZY_LOADING_ERROR_HIDE img")[0]['title']

        # 최종 입력시간
        write_time = browser.find_elements("css selector", "div.media_end_head_info_datestamp_bunch")
        # len(write_time) == 2 이면 수정한 시간 write_time[1]을 가져오고, len(write_time) == 1 이면 입력시간
        if len(write_time) == 1:
            first = soup.select("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")[0]['data-date-time']
            enter = soup.select("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")[0]['data-date-time']
        elif len(write_time) == 2:
            first = soup.select("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")[0]['data-date-time']
            enter = soup.select("span.media_end_head_info_datestamp_time._ARTICLE_MODIFY_DATE_TIME")[0]['data-modify-date-time']
        
        news_content = browser.find_elements("css selector", "div#newsct_article")[0].text.replace("\n", ' ').replace("\'", "")

        col_new = ' '
        data = [col_new, title, company, enter, first, news, news_content]
        news_data.append(data)

    # 겹치는 기사는 제거
    tuple_origin = [tuple(i) for i in news_data]
    unique_data = [list(j) for j in set(tuple_origin)]

    new_df = pd.DataFrame(unique_data)
    new_df.columns = ['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL', '본문']
    new_df = new_df.sort_values(by=['최종입력시간', '입력시간'], ascending=[False, False]).reset_index(drop=True)

    return new_df
