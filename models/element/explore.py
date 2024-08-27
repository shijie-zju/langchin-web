import streamlit as st
from models.functions.utils import *


def button_clicked(button_text):
    st.session_state['chat_input'] = button_text

def create_explore_section(c):
    #c.subheader('功能探索')
    c.markdown('##### 功能探索')
    #c.markdown('---')

    c.button('如何将写好的python代码利用服务器部署到网站中', on_click=button_clicked, args=('如何将写好的python代码利用服务器部署到网站中',), key='explore_button1')
    c.button('今天天气如何,能否外出', on_click=button_clicked, args=('今天天气如何,能否外出', ), key='explore_button2')
    c.button('请作一首诗，要有风、有雨、有歌、还要有小毛驴', on_click=button_clicked, args=('请作一首诗，要有风、有雨、有歌、还要有小毛驴',), key='explore_button3')
