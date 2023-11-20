import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
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
twodaysago = (datetime.now() - timedelta(days=2)).date()


def show_data(real_df, read_df, keyword):
    st.markdown(f"<h6>💡 {keyword} 검색 결과 <strong style='color: #03C85A; display: inline;'>{len(real_df)}</strong>건 </h6>", unsafe_allow_html=True)
            
    read_df = what_is_new(read_df)

    df = show_df(read_df)
    st.data_editor(
        df,
        column_config={
            "URL": st.column_config.LinkColumn(
                "URL",
                help="기사 원문 보려면 더블 클릭하세요.",
                validate="^https://[a-z]+\.streamlit\.app$",
                max_chars=100,
            )
        },
        hide_index=True,
    )

    to_csv_data = real_df[['제목', '언론사', '최종입력시간', '입력시간', 'URL', '본문']]
    csv_data = to_csv_data.to_csv(index=False).encode('utf-8')

    # 파일 다운로드 버튼
    st.download_button(
        label="📥 결과 파일 다운로드",
        data= csv_data,
        file_name=f'download_{keyword}_{today}.csv',
        mime='text/csv',
    )


# 워드 클라우드 만드는 코드
@st.cache_data
def show_wc(file):
    title = file['title']
    news_title = "".join(title)
    real = news_title.replace('.', ' ').replace('"',' ').replace(',',' ').replace("'"," ").replace('·', ' ').replace('=',' ').replace('\n',' ').replace("…", ' ')

    okt = Okt()
    real_tokens = okt.nouns(real)

    vocab = dict(FreqDist(real_tokens))

    font = "./NanumSquareNeo-bRg.ttf"
    wc = WordCloud(font_path=font,
                background_color='white',
                colormap= 'Greens')
    wc = wc.generate_from_frequencies(vocab)
    plt.figure(figsize=(10,10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot()