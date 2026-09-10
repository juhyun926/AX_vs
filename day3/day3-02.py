import pandas as pd
import streamlit as st
import io

st.title('💃🏻k-pop idol 데이터셋 기초탐색')
st.caption('pandas의 head/tail/shape/info/columns를 사용해서 데이터셋의기본 정보를 확입합니다 ')

csv_PATH= '../common/Kpopidolsv3.csv'
upload_file = st.file_uploader('Kpopidolsv3.csv 파일을 직접 업로드 할 수 있습니다.', type='csv')

if upload_file is not None:
    df = pd.read_csv(upload_file)
else:
    try:
        df = pd.read_csv(csv_PATH)
    except FileNotFoundError:
        st.error('❌케이팝 파일을 찾을수가 없습니다🙅‍♀️')
        st.info('같은 경로에 파일을 업로드 하거나 csv파일을 폴더에 새로 고침하세요!')
        df = None

if df is not None :
    st.subheader('1) header(): 데이터의 앞부분 5개 행 미리보기')
    st.dataframe(df.head(), use_container_width=True) #기본행 5개
    
    
    st.subheader('2) tail(): 데이터의 뒷부분 5개 행 미리보기')
    st.dataframe(df.tail(), use_container_width=True) #기본행 5개
    
    st.subheader('3) shape(): 행개수, 열개수')
    col1,col2 = st.columns(2)
    with col1 :
        st.metric('행 개수', f'{df.shape[0]}개')
    with col2:
        st.metric('열 개수', f'{df.shape[1]}개')
    
    
    st.subheader('4) columns: 전체 열(컬럼)이름목록')
        
    st.write(list(df.columns))

    st.subheader('5)info(): 각 열의 자료형과 결측치(NaN) 여부 요약')

    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())
    
      
    
    st.success('기초 정보 확인 끝났습니다. 다음 예제에서 전처리 필터링 하겠습니다🏝️')