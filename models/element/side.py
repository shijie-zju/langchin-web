import streamlit as st


def create_sidebar():
    with st.sidebar:
        st.title('平台介绍')
        st.markdown('---')
        st.markdown('''
        欢迎您使用**Shijie Chat**!

        项目简介：

        **Shijie Chat**是一个基于streamlit所开发的llm应用框架，它拥有对话、本地和在线检索、高级助手等功能，并在平台上开设了角色选择、功能探索等多个板块。

        如果您对我们的项目有任何使用反馈，欢迎联系我们！

        ---
        开发者：宋世杰，陶世杰

        联系方式：1724926804@qq.com 
        ''')
