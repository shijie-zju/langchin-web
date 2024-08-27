import streamlit as st
from models.element.side import create_sidebar
from models.element.control_panel import create_control_panel
from models.element.chat import *
from models.element.explore import create_explore_section

def main():
    #网站命名
    st.set_page_config(
        page_title='Shijie Chat',
        page_icon='',
        layout='wide'  # 上下排列
    )
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ''
    if 'chat_output' not in st.session_state:
        st.session_state.chat_output = ''
    # 创建一个状态变量来跟踪用户的输入
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_is_update' not in st.session_state:
        st.session_state.chat_is_update = False

    c1, c2, c3 = st.columns([1, 3, 0.5])

    create_sidebar()

    control = create_control_panel(c1)
    create_chat_interface(c2, control)
    create_explore_section(c3)


if __name__ == "__main__":
    main()
