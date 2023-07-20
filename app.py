# Bring in deps
import os
from langchain.document_loaders import DirectoryLoader
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory

from constants import QA_FOLDER, OPENAI_API_KEY, RECRUITER_SEQUENCE_MESSAGE_1, RECRUITER_MODEL_BASE_PROMPT
from utils import log_documents

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Reading historical conversations data

loader = DirectoryLoader(QA_FOLDER, glob="**/*.txt", show_progress=True)
docs = loader.load()


print('Docs Number:', len(docs))

# Turning historical conversations into embeddings
embeddings = OpenAIEmbeddings( )
vectors = FAISS.from_documents(docs, embeddings)
retriever = vectors.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Conversational (Chat) Model used
chatModel = ConversationalRetrievalChain.from_llm(llm = ChatOpenAI(temperature=0.0,model_name='gpt-4'),
                                                 retriever=retriever,   chain_type="stuff", return_source_documents=True)

# Memory
recruiterModelMemory = ConversationBufferMemory(input_key='candidate_question', memory_key='recruiter_model_history')


# Prompt templates
recruiterModelPromptTemplate = PromptTemplate(
    input_variables = ['candidate_question', 'knowledge_base_answer'],
    template=RECRUITER_MODEL_BASE_PROMPT
)

# Language Model
llm = ChatOpenAI(temperature=0.9, model_name='gpt-4')
recruiterModel = LLMChain(llm=llm, prompt=recruiterModelPromptTemplate, verbose=True, output_key='recruiter_reply', memory=recruiterModelMemory)



def conversational_chat(query):
    print('------------------\nhistory\n', st.session_state['history'])
    chatModelResult = chatModel({"question": query, "chat_history": st.session_state['history']})
    chatModelResultAnswer = chatModelResult['answer']
    chatModelResultSourceDocuments = chatModelResult['source_documents']
    print('------------------\nchatModelResultAnswer\n', chatModelResultAnswer)
    log_documents(chatModelResultSourceDocuments)
    recuiterModelResult = recruiterModel.run({'knowledge_base_answer': chatModelResultAnswer, "candidate_question": query})
    print('------------------\nrecuiterModelResult\n', recuiterModelResult)
    st.session_state['history'].append((query, recuiterModelResult))

    return recuiterModelResult

if 'history' not in st.session_state:
    st.session_state['history'] = [("", RECRUITER_SEQUENCE_MESSAGE_1)]

if 'generated' not in st.session_state:
    st.session_state['generated'] = [RECRUITER_SEQUENCE_MESSAGE_1]

if 'past' not in st.session_state:
    st.session_state['past'] = []

#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):

        user_input = st.text_input("Reply:", placeholder="Talk with Insquad Auto-Recruiter here", key='input')
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = conversational_chat(user_input)

        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)


if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")
            if len(st.session_state["past"])>i:
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")




#To launch: streamlit run app.py
