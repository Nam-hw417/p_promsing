
# 필요 라이브러리 불러오기

import streamlit as st
import pandas as pd
import numpy as np


# 필요 데이터 불러오기

data = pd.read_csv("CORP_ITEM_EXP.csv", dtype = {"HSCD":str})
map_df = pd.read_csv("HSCD_MTI_MAP_EN.csv", dtype = {'HSCD':str, "MTI_CD1":str, 
                                                  "MTI_CD2":str, "MTI_CD3":str, "MTI_CD4":str, "MTI_CD6":str, "HS_CD10":str})

####  추가 데이터

cqgr = pd.read_csv('CQGR_PROMISING.csv', dtype = {"HSCD":str})
cqgr = cqgr.merge(map_df[['HS_CD10', 'HS_NAME_EN', 'MTI_CD6', 'MTI_6NAME', 'MTI_4NAME', 'MTI_3NAME', 'MTI_2NAME', 'MTI_1NAME']], 
                  how = 'left', left_on ='HSCD', right_on = 'HS_CD10').drop('HS_CD10', axis = 1)






# streamlit 초기값 설정

if 'con' not in st.session_state:
    st.session_state.con = 'Japan'

# streamlit 
        
st.title('Monthly Exports Status by Country')
st.subheader('HSCODE(10) - MTICODE(6) Mapping')


# 국가 리스트 만들기

country_list = data['CON_EN'].unique().tolist()
country_list = [con for con in country_list if con is not np.nan]
country_list.sort()

st.write('Select Country (English)')
st.selectbox(label = 'Country(ENG)',
             options = country_list,
             key = 'con')


        
# 필요 함수작성
@st.cache
def show_promising_items(con):
    df = data[data['CON_EN'] == con]
    df_group = df.groupby(['HSCD', 'EXP_YM']).agg({'BSNO':'count', 'EXP_AMT':'sum'}).reset_index().sort_values(['EXP_YM', 'HSCD'])
    df_group = df_group.merge(map_df, how = "left", left_on ="HSCD", right_on = "HS_CD10")
    # df_group = df_group[['HS_CD10', 'HS_NAME_EN', 'HS_NAME_KR', 'HS_CAT', 'EXP_YM', 'EXP_AMT', 'BSNO', 'MTI_CD6', 'MTI_6NAME']]
    df_group['EXP_AMT'] = df_group['EXP_AMT'].astype(int)
    df_group.drop(['HS_NAME_KR', 'HS_CAT', 'HS_CD10'], axis = 1, inplace = True)
    df_group.rename(columns = {'HSCD':'HS_CD10'}, inplace = True)
    
    return df_group 


# 결과 데이터 프레임

result_df = show_promising_items(st.session_state.con)


# 데이터 프레임 중 샘플 데이터 보여주기


st.subheader('Monthly Export Status: 2021.1 ~ 2023.2')
st.caption('EXP_AMT: Export Amount($), BSNO: Number of Korean Exporting Companies')
st.dataframe(result_df[['HS_CD10', 'EXP_YM', 'EXP_AMT', 'BSNO', 'MTI_CD6', 'MTI_6NAME']].head(20))


# 다운로드 버튼 만들기


@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(result_df)



st.write(f'{st.session_state.con} HS-CODE 10UNIT Monthly Export Performance (2021.1~ 2023.2)') 
excel_file = pd.ExcelWriter('my_excel_file.xlsx', engine = 'xlsxwriter')
result_df.to_excel(excel_file, index = False)
excel_file.save()

button = st.download_button(
    label = 'Download Excel File',
    data = open('my_excel_file.xlsx', 'rb').read(),
    file_name = 'my_excel.file.xlsx',
    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)


#st.download_button(
#    label = 'Download Data as CSV',
#    data = csv,
#    file_name ='items_list.csv',
#    mime = 'text/csv')




@st.cache
def promising_items_by_country(con):
    result_df = cqgr[cqgr['CON_EN'] == con]
    result_df = result_df[result_df['AVG_CNT_Q'] >= 10]
    # result_df['CQGR'] = result_df['CQGR'].apply(lambda x: '{:.2f}%'.format(x*100))
    
    result_df = result_df.sort_values(by ='CQGR', ascending = False)
    result_df[['AVG_CNT_Q', 'AVG_AMT_Q', 'CQGR']] =  result_df[['AVG_CNT_Q', 'AVG_AMT_Q', 'CQGR']].round(2) 
    result_df = result_df.reset_index().drop('index', axis = 1)
    return result_df

promising_df = promising_items_by_country(st.session_state.con)
# promising_df[['AVG_CNT_Q', 'AVG_AMT_Q', 'CQGR']] = promising_df[['AVG_CNT_Q', 'AVG_AMT_Q', 'CQGR']].round(2)

st.subheader('Promising Items (CQGR) : 2021.1Q ~ 2022.4Q')


# st.caption('EXP_AMT: Export Amount($), BSNO: Number of Korean Exporting Companies')
st.dataframe(promising_df[['HSCD', 'AVG_CNT_Q', 'AVG_AMT_Q', 'CQGR', 'HS_NAME_EN','MTI_CD6', 'MTI_6NAME']].head(20))


csv_promising = convert_df(promising_df)

st.write(f'{st.session_state.con} Promising Items : HS-CODE / MTI ') 
st.download_button(
    label = 'Download Data as CSV',
    data = csv_promising,
    file_name ='items_promising.csv',
    mime = 'text/csv')

st.caption('AVG_CNT_Q: Average number of exporting companies per quarter')
st.caption('AVG_AMT_Q: Average export amount per quarter')
st.caption('CQGR: Compound Quarterly Growth Rate')

st.caption('When downloading CSV file, HSCODE 9Units and MTI 5Units are omitted with leading "0"./ Nam.H.W')


# E.O.P

