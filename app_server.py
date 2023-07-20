from flask import Flask, request
from flask_cors import CORS
import os
from langchain.document_loaders import DirectoryLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory

from constants import QA_FOLDER, OPENAI_API_KEY, RECRUITER_SEQUENCE_MESSAGE_1, RECRUITER_MODEL_BASE_PROMPT
from utils import log_documents

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# QA app wrapped into REST API

# Create a new Flask app
app = Flask(__name__)
CORS(app)

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

print('server app ready')

global_history = [("", RECRUITER_SEQUENCE_MESSAGE_1)]

# Define the POST route for /message
@app.route('/message', methods=['POST'])
def conversational_chat():
    query = request.json['message']

    chatModelResult = chatModel({"question": query, "chat_history": global_history})
    chatModelResultAnswer = chatModelResult['answer']
    print('------------------\nchatModelResultAnswer\n', chatModelResultAnswer)
    chatModelResultSourceDocuments = chatModelResult['source_documents']
    log_documents(chatModelResultSourceDocuments)

    recuiterModelResult = recruiterModel.run({'knowledge_base_answer': chatModelResultAnswer, "candidate_question": query})

    global_history.append((query, recuiterModelResult))

    return {
        'response': recuiterModelResult
    }

if __name__ == '__main__':
    app.run(debug=True)
