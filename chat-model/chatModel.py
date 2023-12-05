import os

#INSERT HUGGINGFACE TOKEN
HUGGINGFACEHUB_API_TOKEN = input("Enter HuggingFace token: ")

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.indexes.vectorstore import VectorstoreIndexCreator

#load embedding model
from langchain.embeddings import HuggingFaceEmbeddings

import torch
#Use GPU if available
if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'

model_name = "thenlper/gte-base"
model_kwargs = {'device': device}
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

#lood db that has already been saved locally
docsearch = Chroma(persist_directory="chromadb/documents_chromadb", embedding_function=embeddings)


#for HuggingFace
from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, PreTrainedModel, AutoConfig
from langchain.llms import HuggingFacePipeline

#load model from HuggingFaceHub
from langchain import HuggingFaceHub

repo_id = "tiiuae/falcon-7b-instruct"

llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature":0.2,"max_new_tokens":500, "max_time":None , "num_return_sequences":1, "repetition_penalty":10})


conversationqa_prompt_template = """You are a chatbot having a conversation with a human.
Given the following context, answer the question. If the context does not provide sufficient context to answer the question, say "Sorry, I do not have enough knowledge to answer the question.".

Context:
{context}

{chat_history}Human: {human_input}
AI: """

CONVERSATIONQA_PROMPT = PromptTemplate(
    input_variables=["chat_history", "human_input", "context"], template=conversationqa_prompt_template
)

converseqa = load_qa_chain(
    llm=llm, 
    chain_type="stuff",  
    prompt=CONVERSATIONQA_PROMPT
)

#generate function
def generate(dialog):
    input_query = dialog[-1][1]
    chat_hist = ""
    if len(dialog) > 1:
        for line in dialog[:-1]:
            chat_hist += f'{line[0]}: {line[1]}\n'
    try:
        chat_docs = docsearch.similarity_search(input_query, k=1)
        output = converseqa({"input_documents": chat_docs, "chat_history": chat_hist, "human_input": input_query})["output_text"]
    except:
        output = f'Error with model'
    return output