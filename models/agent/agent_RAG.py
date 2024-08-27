from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import QianfanChatEndpoint, AzureChatOpenAI
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


# Post-processing检索文段的后处理
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def Retrieve(state, _retriever):  # 输入{问题} 进行检索 返回字典{文段，问题}
    """
    Retrieve documents
    Args:
    state (dict): The current graph state 状态字典
    Returns:
    state (dict): New key added to state, documents, that contains
    retrieved documents 返回字典{检索文段和问题}
    """
    print("-------开始检索知识库-------")
    state_dict = state["keys"]  # 读取字典中的keys
    question = state_dict["question"]  # 读取keys中的question
    documents = _retriever.get_relevant_documents(question)  # 检索并返回文段
    # 打印
    docs = format_docs(documents)
    # print(f'知识库检索的文档如下:\n{docs}')

    return {"keys": {"documents": documents, "question": question}}


def generate(state):  # 输入{文段，问题}，进行回答，输出{文段，问题，回复}
    """
    Generate answer
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): New key added to state, generation, that contains LLM
    generation
    """
    print("-------开始基于检索结果和问题回答-------")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]

    # Prompt
    template = """context:{context}

            You are a helpful assistant who knows to solve problems.
            Base on the context and the talk history, try to think step by step. Say Chinese. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            Keep the answer as concise as possible.
            Don't say 'question:' or 'answer:', just say the answer base on the question.
            Use the following pieces of context to answer the question at the end.

            The memory and the question is: {question}
            """
    prompt = ChatPromptTemplate.from_template(template=template)

    # llm = QianfanChatEndpoint(streaming=True)
    llm = ChatOpenAI(temperature=0)
    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {
        "keys": {"documents": documents, "question": question, "generation": generation}
    }


def agent_rag(query_text, control):
    # 嵌入模型和数据库设置
    # 使⽤千帆 embedding bge_large_en 模块
    embeddings_model = OpenAIEmbeddings()
    #embeddings_model = QianfanEmbeddingsEndpoint(model="bge_large_en", endpoint="bge_large_en")
    index = "../chromadata/save_index"
    vectorstore = Chroma(persist_directory=index, embedding_function=embeddings_model)

    _retriever = vectorstore.as_retriever()

    re0 = {"keys": {"question": query_text}}
    jud0 = Retrieve(re0, _retriever)
    print(f'jud:{jud0}')
    res = generate(jud0)
    #print(f'res:{res}')
    response = res['keys']['generation']
    return response