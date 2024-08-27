from langchain_community.chat_models import QianfanChatEndpoint, AzureChatOpenAI
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Dict, TypedDict
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


# Post-processing检索文段的后处理
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def grade_question(state):  # 输入{问题}，判断是否需要文档查询，返回{问题，是否文档查询}

    print("-------正在根据问题判断是否需要文档查询-------")
    state_dict = state["keys"]
    question = state_dict["question"]

    # LLM 原文⽤GPT4 来评分
    model = ChatOpenAI(temperature=0)
    #model = QianfanChatEndpoint(streaming=True)
    llm_with_tool = model

    # Parser
    def parse_input(s):
        if "yes" in s:
            return "yes"
        elif "no" in s:
            return "no"

    # Prompt
    prompt = PromptTemplate(
        template="""You're a judge who can tell if a user's question is a common sense question  \n 
        If you are completely able to answer this question and be feel completely sure the answer is correct, answer 'yes'.\n 
        If you do not feel 100% sure that the answer is correct, answer 'no'.\n
        Give a binary score 'yes' or 'no' score to indicate whether 
you can answer this question directly and completely correctly.Do not answer any other results！\n
        For example:\n
        "Does the sun rise in the East?" This is a common sense question, it does not involve specific information, so reply "yes"\n
"What is the key of openai?", this is a question involving privacy content, can not be answered directly, so reply "no"\n
        Here is the user question: {question} \n
        """,
        input_variables=["question"],
    )

    pro = prompt.invoke({"question": question})
    ans = llm_with_tool.invoke(pro)
    print(f'判断是否要检索:{ans}')
    grade = parse_input(ans.content)

    if grade == "yes":
        print("---该问题能直接回答不需检索---")
        search = "yes"
    else:
        print("---该问题不能直接回答需要检索---")
        search = "no"  # Perform web search设置参数，只要一个不相干，就需要网络查询

    return {
        "keys":
            {"question": question,
             "run_docs_search": search,
             "documents": " ",  # 如果直接生成，也需要传一个空的文档
             }
    }


def decide_to_question(state):  # 输入{问题}，判断能直接回答不再检索，是：返回"response"，否，返回”restriever“

    print("-------正在根据决策内容进行选择-------")
    state_dict = state["keys"]
    question = state_dict["question"]
    search = state_dict["run_docs_search"]
    if search == "yes":
        print("---选择结果：已能够回答问题，直接进行回答---")
        return "response"
    else:
        print("---选择结果：接下来进行数据检索---")
        return "retriever"


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

    #llm = QianfanChatEndpoint(streaming=True)
    llm = ChatOpenAI(temperature=0)
    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"context": documents, "question": question})

    return {
        "keys": {"documents": documents, "question": question, "generation": generation}
    }


def grade_documents(state):  # 输入{问题，文段}，判断每条检索文段的相关性，返回{问题，相关文段，是否网络查询}
    """
    Determines whether the retrieved documents are relevant to the question.确定检索的文档是否与问题相关。
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Updates documents key with relevant documents
    """
    print("-------正在判断每段文档的相关性-------")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]

    # LLM 原文⽤GPT4 来评分
    model = ChatOpenAI(temperature=0)
    #model = QianfanChatEndpoint(streaming=True)
    llm_with_tool = model

    # Parser
    def parse_input(s):
        if "yes" in s:
            return "yes"
        elif "no" in s:
            return "no"

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved
document to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the
user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the
document is relevant to the question.Do not answer any other results！""",
        input_variables=["context", "question"],
    )
    # Score
    filtered_docs = []
    search = "no"  # Default do not opt for web search to supplement retrieval不需要网络检索
    for d in documents:  # 对每项文段进行判断
        # score = chain.invoke({"question": question, "context": d.page_content})
        pro = prompt.invoke({"question": question, "context": d.page_content})
        ans = llm_with_tool.invoke(pro)
        grade = parse_input(ans.content)

        print(f'检索得到的文档为：{d}')
        if grade == "yes":
            print("---本段文档相关,将保留---")
            filtered_docs.append(d)  # 筛选出有相关性的文段
        else:
            print("---本段文档不相关,不会保留---")
            search = "yes"  # Perform web search设置参数，只要一个不相干，就需要网络查询
            continue
    return {
        "keys": {
            "documents": filtered_docs,
            "question": question,
            "run_web_search": search,
        }
    }


def transform_query(state):  # 输入{问题，文段}，进行问题重述，返回{更好的问题，文段}
    """
    Transform the query to produce a better question.
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): Updates question key with a re-phrased question
    """
    print("-------正在进行问题重述-------")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]

    # Create a prompt template with format instructions and the query
    prompt = PromptTemplate(
        template="""You are generating questions that is well optimized for
retrieval. \n 
        Look at the input and try to reason about the underlying sematic
intent / meaning. \n 
        Here is the initial question:
        \n ------- \n
        {question} 
        \n ------- \n
        Formulate an improved question,Do not answer or don no say anything else, just restate the question and just ask！
        The new question is: """,
        input_variables=["question"],
    )

    # Grader
    model = ChatOpenAI(temperature=0)
    #model = QianfanChatEndpoint(streaming=True)
    # model = QianfanChatEndpoint(model="ERNIE-Bot-4")

    # Prompt
    chain = prompt | model | StrOutputParser()
    better_question = chain.invoke({"question": question})
    print(f'重述后的问题为:{better_question}')
    return {"keys": {"documents": documents, "question": better_question}}


def web_search(state):  # 输入{问题，文段}，进行检索，返回{问题，检索后扩充的文段}
    """
    Web search based on the re-phrased question using Tavily API.

    Args:
    state (dict): The current graph state
    Returns:
    state (dict): Updates documents key with appended web results
    """
    print("-------正在进行联网检索-------")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]
    web_results = '未检索'
    # tool = TavilySearchResults()
    # docs = tool.invoke({"query": question})
    # web_results = "\n".join([d["content"] for d in docs])
    # web_results = Document(page_content=web_results)
    # documents.append(web_results)
    print(f'检索结果为:{web_results}')
    return {"keys": {"documents": documents, "question": question}}


def decide_to_generate(state):  # 输入{问题，文段，是否网络搜索}，是：返回"transform_query"，否，返回”generate“
    """
    Determines whether to generate an answer or re-generate a question for web
search.决定生成答案还是重新搜索
    Args:
        state (dict): The current state of the agent, including all keys.
    Returns:
        str: Next node to call
    """
    print("-------正在根据查询决策进行选择-------")
    state_dict = state["keys"]
    question = state_dict["question"]
    filtered_documents = state_dict["documents"]
    search = state_dict["run_web_search"]
    if search == "yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print("---选择结果：接下来进行问题重述和网络检索---")
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---选择结果：已能够回答问题，直接进行回答---")
        return "generate"


class GraphState(TypedDict):
    """
    Represents the state of our graph.
    Attributes:
        keys: A dictionary where each key is a string.
    """
    keys: Dict[str, any]


def agent_all(query_text, control):
    # 嵌入模型和数据库设置
    # 使⽤千帆 embedding bge_large_en 模块
    embeddings_model = OpenAIEmbeddings()
    #embeddings_model = QianfanEmbeddingsEndpoint(model="bge_large_en", endpoint="bge_large_en")
    index = "../chromadata/save_index"
    vectorstore = Chroma(persist_directory=index, embedding_function=embeddings_model)

    _retriever = vectorstore.as_retriever()

    # go_on = True
    # while go_on:
    #     query_text = input("你的问题：")
    #
    #     if 'exit' in query_text:
    #         break
    #print("AI需要回答的问题[{}]\n".format(query_text))

    re0 = grade_question({"keys": {"question": query_text}}) #分析问题是否需要检索
    re1 = decide_to_question(re0)
    if re1 == "response":
        res = generate(re0)
    else:  # “retriever”
        jud0 = Retrieve(re0, _retriever)
        jud1 = grade_documents(jud0)
        jud2 = decide_to_generate(jud1)
        if jud2 == "transform_query":
            a1 = transform_query(jud1)
            a2 = web_search(a1)
            res = generate(a2)
        else:
            res = generate(jud1)
    #print(f'res:{res}')
    response = res['keys']['generation']
    return response