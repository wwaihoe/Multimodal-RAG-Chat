import os
import requests
import json

from LLM import LlamaCPP

retrievalName = "retrieval-model"
retrievalPort = "8002"

import torch
#Use GPU if available
if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'




class QAChain:
    def __init__(self, vectorStoreURL, llm):
        self.vectorStoreURL = vectorStoreURL
        self.llm = llm
        

    def generate(self, dialog):
        input_query = dialog["dialog"][-1]["message"] if len(dialog["dialog"]) > 0 else ""
        chat_history = ""
        if len(dialog["dialog"]) > 1:
            for line in dialog["dialog"][:-1]:
                #chat_hist += f'{line["sender"]}: {line["message"]}\n'

                #llama3 template
                chat_history += f"""<|start_header_id|>{line["sender"]}<|end_header_id|>
                
                {line["message"]}<|eot_id|>
                """
        try:
            res = requests.post(f"{self.vectorStoreURL}/retrieve", json={"query":  input_query})
            context = res.json()["doc"]
            conversationqa_prompt_template = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

            You are a helpful AI assistant having a conversation with a human<|eot_id|>
            <|start_header_id|>user<|end_header_id|>

            Use the following context to answer the human's question. Provide a single clear and concise response. If the context does not provide sufficient context to answer the question, say "Sorry, I do not have enough knowledge to answer the question.". 
            Context: {context}. 
            Chat history: {chat_history}.<|eot_id|>
            <|start_header_id|>user<|end_header_id|>
                
            {input_query}<|eot_id|> 
            <|start_header_id|>assistant<|end_header_id|>

            """

            output = self.llm.generate(conversationqa_prompt_template)
        except:
            output = f'Error with model'
        return output



# Load Llama 3 8b with default settings
llm = LlamaCPP(model_dir="../models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")

QAChainModel = QAChain(f"http://{retrievalName}:{retrievalPort}", llm)