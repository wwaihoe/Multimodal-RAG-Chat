import os
import requests
import json


from langchain.prompts import ChatPromptTemplate
#for HuggingFace
from langchain.llms import HuggingFaceHub
#for OpenAI
from langchain.llms import OpenAI

retrievalURL = "retrieval-model"
retrievalPort = "8002"

import torch
#Use GPU if available
if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'

repo_id = "mistralai/Mistral-7B-v0.1"

llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature":0.2,"max_new_tokens":500, "max_time":None , "num_return_sequences":1, "repetition_penalty":10})
#llm = OpenAI()

conversationqa_prompt_template = """You are a chatbot having a conversation with a human.
Given the following context, answer the question. If the context does not provide sufficient context to answer the question, say "Sorry, I do not have enough knowledge to answer the question.".

Context:
{context}

{chat_history}Human: {human_input}
AI: """

CONVERSATIONQA_PROMPT = ChatPromptTemplate.from_template(template=conversationqa_prompt_template)


class QAChain:
    def __init__(self, vectorStoreIP, llm, prompt):
        self.vectorStoreIP = vectorStoreIP
        self.chain = prompt | llm

    def generate(self, dialog):
        input_query = dialog["dialog"][-1]["message"] if len(dialog["dialog"]) > 0 else ""
        chat_hist = ""
        if len(dialog["dialog"]) > 1:
            for line in dialog["dialog"][:-1]:
                chat_hist += f'{line["sender"]}: {line["message"]}\n'
        try:
            res = requests.post(f"{self.vectorStoreIP}/retrieve", json={"query":  input_query})
            chat_docs = res.json()["doc"]
            output = self.chain.invoke({"context": chat_docs, "chat_history": chat_hist, "human_input": input_query})
        except:
            output = f'Error with model'
        return output

QAChainModel = QAChain(f"http://{retrievalURL}:{retrievalPort}", llm, CONVERSATIONQA_PROMPT)