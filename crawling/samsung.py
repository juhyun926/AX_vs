import time
from bs4 import BeautifulSoup
import openpyxl
import pandas as pd
import requests

code = '016360'  # 삼성증권 종목코드
headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

data = []

# 1~5페이지 수집 (페이지당 10거래일 = 총 50거래일)
for page in range(1, 6):
    url = f'https://finance.naver.com/item/sise_day.naver?code={code}&page={page}'
    res = requests.get(url, headers=headers)
    res.encoding = 'cp949'  # 한글 깨짐 방지

    soup = BeautifulSoup(res.text, 'html.parser')

    # 일별 시세 테이블 내 모든 행(tr) 탐색
    rows = soup.select('table.type2 tr')

    for tr in rows:
        cols = tr.select('td')

        # 데이터가 없는 빈 구분선 행(cols 개수가 적은 경우) 건너뛰기
        if len(cols) < 7:
            continue

        date = cols[0].text.strip()
        if not date:  # 날짜 텍스트가 비어있으면 건너뛰기
            continue

        close_price = cols[1].text.strip()  # 종가
        diff = cols[2].text.strip()  # 전일비
        open_price = cols[3].text.strip()  # 시가
        high_price = cols[4].text.strip()  # 고가
        low_price = cols[5].text.strip()  # 저가
        volume = cols[6].text.strip()  # 거래량

        data.append([
            date,
            close_price,
            diff,
            open_price,
            high_price,
            low_price,
            volume,
        ])

    time.sleep(0.3)  # 요청 간격 조절

# DataFrame 생성 및 엑셀 저장
columns = ['날짜', '종가', '전일비', '시가', '고가', '저가', '거래량']
df = pd.DataFrame(data, columns=columns)

excel_filename = 'samsung_daily_bs4.xlsx'
df.to_excel(excel_filename, index=False)

print(f'총 {len(df)}건 수집 완료 -> {excel_filename} 파일로 저장되었습니다.')
print(df.head())