import streamlit as st
from PIL import Image
import numpy as np


def uploader_file(c1):
    uploaded_file = c1.file_uploader(label='', type=["jpg", "jpeg", "png"], key='file_uploader')

    return uploaded_file


def create_control_panel(c):
    # Title for the control panel section
    #c.subheader("控制面板")
    c.markdown('''
    #### 控制面板
    ##### 角色选择
    ''')

    character = c.radio(
        label='请选择你想要对话的角色:',
        options=('A:仅对话', 'B:本地检索', 'C:上传文件检索', 'D:联网查询', 'E:高级助手'),
        index=0,
        format_func=str,
        help='不同角色可解锁不同功能'
    )

    # 文档上传板块
    cdoc = c.markdown('''
        ##### 文档上传
        ''')
    file = ''
    file = uploader_file(c)
    print(f'file:{file}')

    # 参数调节板块
    c.markdown('''
        ##### 参数调节
        ''')
    max_length = c.slider(label='请设置AI回复内容的最大长度',
                           min_value=0,
                           max_value=200,
                           value=100,
                           step=1,
                           help="拖动滑块来限制AI回复内容长度"
                           )

    temperature = c.slider(label='请设置llm输出的灵活度',
                            min_value=0.0,
                            max_value=1.0,
                            value=1.0,
                            step=0.1,
                            help="即调整llm的temperature值"
                            )

    return {'character': character, 'file': file, 'max_length': max_length, 'temperature': temperature}

