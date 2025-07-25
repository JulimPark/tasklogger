import streamlit as st
from supabase import create_client
import os,time
# import dotenv
import ast
st.set_page_config(page_title="KIOT 업무일지 기록", page_icon=':balloon',layout='centered')

# dotenv.load_dotenv()
# SUPA_URL = os.getenv('SUPA_URL')
# SUPA_KEY = os.getenv('SUPA_KEY')

# members = os. getenv('MEMBERS')
# passset = os.getenv('PASSSETS')

# 배포용
SUPA_URL = st.secrets['SUPA_URL']
SUPA_KEY = st.secrets['SUPA_KEY']

members = st.secrets['MEMBERS']
passset = st.secrets['PASSSETS']
# members = ast.literal_eval(members)
# passset = ast.literal_eval(passset)


@st.cache_resource
def init_connection():
    url = SUPA_URL
    key = SUPA_KEY
    return create_client(url, key)

def data_load(user:str=None):
    if user==None:
        response = supabase.table('taskLOG').select('*').match({'name':st.session_state.username}).execute()
    else:
        response = supabase.table('taskLOG').select('*').execute()
        
    return response.data

supabase = init_connection()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

if st.session_state.logged_in == False:

    with st.form('로그인'):
        st.subheader(':blue[KIOT 빅데이터팀] 업무일지')
        cols = st.columns([1,4,1])
        with cols[1]:
            name = st.text_input('ID')
            password = st.text_input('Password',type='password')
            loginbtn = st.form_submit_button(label='Login',use_container_width=True)

    if loginbtn:
        if name in members:
            if password == passset[members.index(name)]:
                st.session_state.logged_in = True
                st.session_state.username = name
                st.rerun()
            else:
                st.error('비밀번호가 틀렸습니다.')
        else:
            st.error('등록된 사용자가 아닙니다.')

if st.session_state.logged_in == True:
    with st.form(f'업무일지 작성',clear_on_submit=True):
        st.subheader(f':blue[업무일지 작성({st.session_state.username}님)]')
        cols = st.columns(2)
        with cols[1]:
            date = st.date_input(label='날짜')
        tasklog = st.text_area(label=':red[업무내용]',height=200)
        fileLocation = st.text_area(label='파일위치/특이사항/건의사항',height=100)
        cols = st.columns(3)
        with cols[1]:
            oklog = st.form_submit_button(label='기록',use_container_width=True)
        if oklog:
            if tasklog=="":
                st.info("업무내용은 필수로 입력해야 합니다")
                time.sleep(2)
                st.rerun()
            else:
                res = supabase.table('taskLOG').insert({
                    'name': st.session_state.username,
                    'tasklog':tasklog,
                    'date': f"{date.year}/{format(date.month,'02')}/{format(date.day,'02')}",
                    'etc':fileLocation
                }).execute()
                st.success('입력되었습니다.')
                time.sleep(2)
                st.rerun()
            
    with st.expander(label='업무기록확인',):
        if st.session_state.username == '박주림':
            df = data_load(user=st.session_state.username)
        else:
            df = data_load()
        for i,var in enumerate(df):
            df[i].pop('created_at')
        df = sorted(df, key=lambda x: x['date'],reverse=True)

        st.dataframe(df)
        
