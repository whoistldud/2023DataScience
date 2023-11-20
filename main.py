import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 다른 파일에서 정의한 함수 import 하기
from crawl_data import crawl_data
from mapianet import crawl_search
from open_file import open_data
from show_data import show_data, show_wc

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from nltk import FreqDist
st.set_option('deprecation.showPyplotGlobalUse', False)

# 스타일링 함수
def highlight_rows(row):
    if row['new'] == '🆕':
        return ['background-color: #E6F8E0'] * len(row)
    else:
        return [' '] * len(row)
    
# 화면에 띄울 DataFrame 만드는 함수
def show_df(data):
    column_names = data.columns.tolist()
    if 'new' in column_names:
        # 화면에 보여줄 데이터는 본문 빼고, '최종입력시간' 기준으로 최근 날짜가 위로 오게 정렬
        df = data[['new','제목', '언론사', '최종입력시간', '입력시간', 'URL']].sort_values('최종입력시간', ascending=False)
        df['최종입력시간'] = pd.to_datetime(df['최종입력시간'])
        # df = pd.DataFrame(df).reset_index()
        styled_df = df.style.apply(highlight_rows, axis=1)
        return styled_df
    else:
        df = data[['제목', '언론사', '최종입력시간', '입력시간', 'URL']].sort_values('최종입력시간', ascending=False)
        df['최종입력시간'] = pd.to_datetime(df['최종입력시간'])
        # df = pd.DataFrame(df).reset_index()
        styled_df = df.style.apply(highlight_rows, axis=1)
        return styled_df

# 새로운 데이터에 🆕 표시하기
def what_is_new(df):
    # 날짜 형식으로 변환
    df['최종입력시간'] = pd.to_datetime(df['최종입력시간'])
    df['new'] = '  '
    # '최종입력시간'이 twodaysago보다 큰 경우에 '🆕' 값 추가
    df.loc[df['최종입력시간'].dt.date > twodaysago, 'new'] = '🆕'

    return df

today = datetime.now().date().strftime('%Y-%m-%d').replace('-', ".")
yesterday = (datetime.now() - timedelta(1)).date().strftime('%Y-%m-%d').replace('-', ".")
twodaysago = (datetime.now() - timedelta(days=2)).date()

## ------------  화면에 보이는 코드 시작 -----------------
st.markdown("<h1 style='text-align: center; color: #03C85A;'>#03C85A</h1>", unsafe_allow_html=True)

columns = st.columns(3)
with columns[0]:
    btn_hyperX = st.button("하이퍼클로바X")

with columns[1]:
    btn_cloverX = st.button('클로바X')

with columns[2]:
    btn_cue = st.button('큐(Cue:)')

with st.form("다른 키워드가 궁금하다면?", clear_on_submit= True):
    keyword = st.text_input("다른 키워드가 궁금하다면?",placeholder="검색어를 입력하세요.")
    submitted = st.form_submit_button("Search!")

# 하이퍼클로바X 버튼이 눌렸을 경우
if btn_hyperX:
    word = "하이퍼클로바X"
    ex_data = open_data(1)

    max_first = ex_data['입력시간'].max()
    max_first_date = datetime.strptime(max_first, '%Y-%m-%d %H:%M:%S').date()
    crawl_start = (max_first_date + timedelta(days=1)).strftime('%Y-%m-%d').replace('-', ".")

    new_df = crawl_data(word, crawl_start, today)

    if len(new_df) == 0: # 데이터가 없는 경우
        real_df = pd.DataFrame(pd.read_excel("./project_data1.xlsx"))
        read_df = real_df[['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL']]
        show_data(real_df, read_df, word)

    else:
        # 새로운 데이터를 기존 데이터프레임에 추가 
        update_data = pd.concat([ex_data, new_df], ignore_index=True)
        update_data = update_data.drop_duplicates(subset = ['입력시간', 'URL'])
        # 업데이트된 DataFrame을 파일에 저장
        update_data.to_excel("./project_data1.xlsx", index=False)

        # 저장된 크롤링 결과를 읽어와서 출력
        real_df = pd.DataFrame(pd.read_excel("./project_data1.xlsx"))
        read_df = real_df[['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL']]
        st.info('업데이트된 데이터가 있습니다.', icon="📌")
        show_data(real_df, read_df, word)

# 클로바X 버튼이 눌렸을 경우
elif btn_cloverX:
    word = "클로바X"
    ex_data = open_data(2)
    max_first = ex_data['입력시간'].max()
    max_first_date = datetime.strptime(max_first, '%Y-%m-%d %H:%M:%S').date()
    crawl_start = (max_first_date + timedelta(days=1)).strftime('%Y-%m-%d').replace('-', ".")

    new_df = crawl_data(word, crawl_start, today)

    if len(new_df) == 0:
        real_df = pd.DataFrame(pd.read_excel("./project_data2.xlsx"))
        read_df = real_df[['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL']]
        
        show_data(real_df, read_df, word)

    else:
        update_data = pd.concat([ex_data, new_df], ignore_index=True)
        update_data = update_data.drop_duplicates(subset = ['입력시간', 'URL'])
        update_data.to_excel("./project_data2.xlsx", index=False)

        # 저장된 크롤링 결과를 읽어와서 출력
        real_df = pd.DataFrame(pd.read_excel("./project_data2.xlsx"))
        read_df = real_df[['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL']]
        
        st.info('업데이트된 데이터가 있습니다.', icon="📌")
        show_data(real_df, read_df, word)

# 큐(Cue:) 버튼이 눌렸을 경우
elif btn_cue:
    word = "큐"
    ex_data = open_data(3)

    max_first = ex_data['입력시간'].max()
    max_first_date = datetime.strptime(max_first, '%Y-%m-%d %H:%M:%S').date()
    crawl_start = (max_first_date + timedelta(days=1)).strftime('%Y-%m-%d').replace('-', ".")

    new_df = crawl_data(word, crawl_start, today)

    if len(new_df) == 0:
        
        real_df = pd.DataFrame(pd.read_excel("./project_data3.xlsx"))
        read_df = real_df[['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL']]
        
        show_data(real_df, read_df, word)

    else:
        update_data = pd.concat([ex_data, new_df], ignore_index=True)
        update_data = update_data.drop_duplicates(subset = ['입력시간', 'URL'])
        update_data.to_excel("./project_data3.xlsx", index=False)

        real_df = pd.DataFrame(pd.read_excel("./project_data3.xlsx"))
        read_df = real_df[['new', '제목', '언론사', '최종입력시간', '입력시간', 'URL']]
        
        st.info('업데이트된 데이터가 있습니다.', icon="📌")
        show_data(real_df, read_df, word)

elif submitted:
    if keyword != '':
        now_date = datetime.now()
        crawl_start = (now_date - timedelta(days=7)).strftime('%Y-%m-%d').replace('-', ".")
        new_df = crawl_data(keyword, crawl_start, today)

        if len(new_df) == 0:
            st.warning("해당하는 데이터를 찾을 수 없습니다.", icon="⚠️")
            
        else:
            csv_data = new_df[['제목', '언론사', '최종입력시간', '입력시간', 'URL', '본문']]
            csv_data = csv_data.to_csv(index=False).encode('utf-8')
            new_df = what_is_new(new_df)
            other_df = show_df(new_df)
            
            st.data_editor(
            other_df,
            column_config={
                "URL": st.column_config.LinkColumn(
                    "URL",
                    help="접속하려면 더블 클릭하세요.",
                    validate="^https://[a-z]+\.streamlit\.app$",
                    max_chars=100,
                )
            },
            hide_index=True,
        )
        
        # 파일 다운로드 버튼
        st.download_button(
            label="📥 결과 파일 다운로드",
            data= csv_data,
            file_name=f'download_{keyword}_{today}.csv',
            mime='text/csv'
        )

st.divider()


# 마피아넷에서 가져온 검색수
st.markdown("<h5 style='color: #03C85A;'>네이버 월간 검색수</h5>", unsafe_allow_html=True)

cue, cloverX, hypercloverX = crawl_search()
# st.subheader("네이버 월간 검색 수")
columns = st.columns(3)
with columns[0]:
    st.metric('하이퍼클로바X', value=f'{hypercloverX:,.0f}')

with columns[1]:
    st.metric('클로바X', value=f'{cloverX:,.0f}')

with columns[2]:
    st.metric('큐(Cue:)', value=f'{cue:,.0f}')



### 여기부터 워드 클라우드 코드

st.divider()

st.markdown("📌 최근 7일 내 수집한 기사 제목으로 생성한 워드 클라우드입니다.")
# 크롤링한 기사 제목들로 워드 클라우드 만들기
for_wc = pd.read_excel('./2023.11.11_2023.11.18_AItitle.xlsx')
show_wc(for_wc)


st.divider()


### ------ 발표 관련 --------
st.markdown("<h6 style='color: #088A08;'>네이버 클라우드 | Service & Business | Product Development</h6>", unsafe_allow_html=True)
st.markdown("월간 검색수 🔗URL : https://www.ma-pia.net/keyword/keyword.php")