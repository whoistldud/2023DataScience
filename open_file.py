import pandas as pd

# 데이터 파일 불러오는 함수
def open_data(val):
    ex_data = pd.read_excel(f"./project_data{val}.xlsx")

    return ex_data