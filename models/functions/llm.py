from typing import List

from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
import streamlit as st
from models.functions.utils import *
from models.agent.agent_chat import *
from models.agent.agent_RAG import *
from models.agent.agent_RAG_online import *
from models.agent.agent_Web import *
from models.agent.agent_all import *

class LLM(object):
    def __init__(self, **kwargs): #用kwargs允许传入任意数量的参数到类的构造器中
        self.character = kwargs.pop('character', 0) #pop实现了对字典剔出其中character键的值，如果没有就默认0，然后赋给character
        self.file = kwargs.pop('file', None)
        self.max_length = kwargs.pop('max_length', 100)
        self.temperature = kwargs.pop('temperature', 1)

    # 主要函数，获取输入和控制台的参数，根据参数选择在不同的llm路径下进行
    def response(self, text: str):
        #提取出角色来，进行后续判断
        character = self.character
        non_text_output = r'F:\python\llm-math\langchain_web4\UI\dog.jpg'

        chat_memory = 'question:\n'
        epoch = len(st.session_state['chat_history'])
        for index in range(epoch):
            q = st.session_state['chat_history'][index][0]
            a = st.session_state['chat_history'][index][1]
            chat_memory = chat_memory + q + '\nanswer:\n' + a + '\nquestion: \n'
        text_memory = chat_memory + text + '\nanswer:'
        print(f'memory:\n{text_memory}')
        if character == 'A:仅对话':
            user_output = agent_chat(text_memory, character)
            #non_text_output = ''

        elif character == 'B:本地检索':
            user_output = agent_rag(text_memory, character)
            #non_text_output = ''

        elif character == 'C:上传文件检索':
            user_output = agent_rag_online(text_memory, character)
            #non_text_output = ''

        elif character == 'D:联网查询':
            user_output = agent_web(text_memory, character)
            #non_text_output = ''

        else:
            user_output = agent_all(text_memory, character)
            #non_text_output = ''

        return user_output, non_text_output

    # def query(self, text: str) -> List[str]:
    #     return [text]
    #
    # def grade_question(self, text: str):
    #     output =  text * 2
    #     return output
    #
    # def figure(self):
    #     return r'C:\Users\tsj15\Desktop\1709464597925.jpg'

    # @staticmethod
    # def _langchain_format(text):
    #     return {'keys': {'question': text}}

