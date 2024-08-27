from langchain_community.chat_models import QianfanChatEndpoint

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


def agent_chat(text, control):
    template = """You are a helpful assistant who knows to solve problems.
    Base on the talk history, try to think step by step. Say Chinese. 
    Don't say 'question:' or 'answer:', just say the answer base on the question.
    The memory and the question is {query}"""
    human_template = ""

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI()
    #llm = QianfanChatEndpoint(streaming=False)
    output_parser = StrOutputParser()
    #output_parser = MathOutputParser()

    chain = prompt | llm | output_parser
    res = chain.invoke({"query": text})
    print(res)
    return res