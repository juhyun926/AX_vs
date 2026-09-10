# 인코딩 자동 감지 + 한글 폰트 막대그래프
# 여러 인코딩(' utf 8-sig ', 'cp949','euc-kr')순서대로 시도
# 내가 쓸 폰트 같은 경로에 있어야 함
# 객실 등급별 생존을 막대그래프 생성후 그림으로 저장 chart.png
# 실행 streamlit run day3-03.py


import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

st.title('📊인코딩 자동감지+한글 폰트 막대 그래프(Titanic연습)')
st.caption('여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실등급별 생존율')

csv_PATH = os.path.join(os.path.dirname(__file__), 'titanic_cleaned.csv')

def read_csv_with_auto_encoding(file_path: str, **kwargs):
    """여러 인코딩을 순서대로 시도하여 CSV 파일을 읽어오는 함수"""
    encodings = ["utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            st.write(f'{encoding}으로 읽었습니다')
            return df, encoding  # df와 encoding 2개 반환
        except (UnicodeDecodeError, UnicodeError):
            continue

    raise ValueError(f'지원하는 인코딩으로 파일을 디코딩할 수 없습니다: {file_path}')

# 1) 인코딩 자동 감지로 csv 읽기
st.subheader('1) 인코딩 자동 감지')
df, used_encoding = read_csv_with_auto_encoding(csv_PATH)

# 객실등급 별 생존율 집계
Pclass_survival_rate = df.groupby('Pclass')['Survived'].mean().sort_index()
st.dataframe((Pclass_survival_rate * 100).round(1).rename('생존율(%)'))

st.markdown('---')
st.subheader('3) 객실 등급별 생존율 막대그래프')

# 윈도우 기본 한글 폰트 설정 (별도 폰트 파일 불필요)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 막대 그래프 그리기
fig, ax = plt.subplots(figsize=(8, 5))
(Pclass_survival_rate * 100).plot(kind='bar', color="#FDCFE4", ax=ax)
ax.set_title('객실 등급별 생존율')
ax.set_xlabel('객실등급(Pclass)')
ax.set_ylabel('생존율(%)')

st.pyplot(fig)

output_png = os.path.join(os.path.dirname(__file__),'chart.png')
fig.savefig(output_png)