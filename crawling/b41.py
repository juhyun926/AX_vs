from bs4 import BeautifulSoup
import openpyxl
import pandas as pd
import requests

data = []

for i in range(1, 5): #페이지 수 만큼 반복하면 됨 for i in range(1, 10)
    response = requests.get(f'https://startcoding.pythonanywhere.com/basic?page={1}')
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    items = soup.select('.product')

    for item in items:
        category = item.select_one('.product-category').text  # 카테고리
        category_name = item.select_one('.product-name').text  # 상품명
        category_link = item.select_one('.product-name > a').attrs['href']
        price = item.select_one('.product-price').text.split('원')[0].replace(',',"") # 가격

        data.append([category, category_name, category_link, price])

        print(category, category_name, category_link, price)

df = pd.DataFrame(data, columns=['카테고리', '상품명', '상세페이지링크', '가격'])
df.to_excel('data.xlsx', index=False)