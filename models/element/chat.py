import random
import time
import streamlit as st
from models.functions.utils import *
from models.functions.llm import LLM
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


def on_send_clicked(llm):
    user_input = st.session_state['chat_input']
    if user_input:
        user_output, non_text_output = llm.response(user_input)  # 语言模型,输入问题和控制参数，输出回答和非文本回复

        st.session_state.chat_history.append([user_input, user_output])

        st.session_state.chat_input = ""
        st.session_state.chat_is_update = True
        #print(f'non_text:{non_text_output}')
        st.session_state['chat_output'] = non_text_output


def _clear():
    st.session_state.chat_history.clear()
    st.session_state['chat_input'] = ""
    st.session_state['chat_output'] = None


def stream_data(message):
    for word in random_split_preserved_order(message, min_chunk=1, max_chunk=3):
        yield word + ""
        time.sleep(random.uniform(0, 0.1))


def write_direct(c21, message):
    #c21.write(f"输入： {message[0]}")
    c21.markdown(f"<p style='text-align: right; 'font-size'=0.1px;>{message[0]}</p>", unsafe_allow_html=True)
    c21.write(f"{message[1]}")
    # for text in message[1]:
    #     c21.write(text + '\n')


def write_stream(c21, message):
    #c21.write(f"输入： {message[0]}")
    #c21.write(f"输出：")
    # for text in message[1]:
    #     c21.write_stream(stream_data(text))
    c21.markdown(f"<p style='text-align: right; 'font-size'=0.1px;>{message[0]}</p>", unsafe_allow_html=True)
    c21.write_stream(stream_data(message[1]))

def build_widgets(c, llm):
    # title
    #c.subheader('Chat')
    c.markdown('#### Chat')
    #c.markdown('---')
    # 两个输出窗口
    col1, col2 = c.columns([3, 2])
    # 输入框
    c.text_area("请输入内容", value=st.session_state.chat_input, key='chat_input')

    # button
    button1, button2 = c.columns([1, 1])
    button1.button('发送', on_click=on_send_clicked, key='seed', args=(llm,))
    button2.button('清除', on_click=_clear, key='clear')

    return col1, col2


def greet(control):
    character = control['character']
    if character == 'A:仅对话':
        say = '我是您的个人帮助助手，虽然我懂的不多但会尽力帮助您解决问题'
    elif character == 'B:本地检索':
        say = '我是您的个人帮助助手，我将基于数据库为您答疑解惑'
    elif character == 'C:上传文件检索':
        say = '我是您的个人帮助助手，欢迎您上传文件，我将基于上传的文件进行学习和回答'
    elif character == 'D:联网查询':
        say = '我是您的个人帮助助手，我可以联网帮助您解决问题'
    else:
        say = '我是您的个人帮助助手，我将基于我的一切智慧为您答疑解惑'
    return say

def create_chat_interface(c, control):
    # character = control['character']
    # file = control['file']
    # max_length = control['max_length']
    # temperature = control['temperature']

    llm = LLM(**control)
    col1, col2 = build_widgets(c, llm)

    chat_container = col1.container(height=350)
    #打印第一句
    first_greet = greet(control)
    chat_container.write(f"{first_greet}")
    # 将chat_history中的内容输出，如果不是最后 一轮对话，则直接打印到col板块的容器中，如果是最后一轮且is_updata是True，就流式打印
    epoch = len(st.session_state['chat_history'])
    for index in range(epoch):
        message = st.session_state['chat_history'][index]  # [user_input, user_output]
        if index != epoch - 1:
            write_direct(chat_container, message)
        else:
            if st.session_state.chat_is_update:
                write_stream(chat_container, message)
                st.session_state.chat_is_update = False
            else:
                write_direct(chat_container, message)

    # figure
    with col2:
        if st.session_state.chat_output:
            image = Image.open(st.session_state.chat_output)
            col2.image(image, use_column_width=True, caption='Uploaded Image')
        # if file:
        #     image = Image.open(file)
        #     col2.image(image, use_column_width=True, caption='Uploaded Image')

