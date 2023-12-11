import os

#INSERT HUGGINGFACE TOKEN
#HUGGINGFACEHUB_API_TOKEN = input("Enter HuggingFace token: ")
HUGGINGFACEHUB_API_TOKEN = "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"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
#for HuggingFace
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFaceHub


chroma_client = chromadb.PersistentClient(path="/chromadb/documents_chromadb")
collection = chroma_client.get_or_create_collection(name="chroma_collection")

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


class chromaDB:
    def __init__(self, chroma_client, collection_name, embeddings):
        self.langchain_chroma = Chroma(
            client=chroma_client,
            collection_name=collection_name,
            embedding_function=embeddings,
        )
        self.currID = 0
    def splitDocument(self, file):
        reader = PdfReader(file)
        page_delimiter = '\n'
        docu = ""
        #exclude cover page and table of contexts
        for page in reader.pages:
            page_text = page.extract_text()
            page_text += page_delimiter
            docu += page_text
        #split document using recursive splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap  = 300,
            length_function = len,
        )
        texts = text_splitter.split_text(docu)
        return texts
    
    def addToVectorStore(self, file, fileName):
        texts = self.splitDocument(file)
        for i in range(len(texts)):
            self.langchain_chroma.add_texts(
                ids=[str(self.currID)],
                texts=[texts[i]],
                metadatas=[{"source": fileName}]
            )
            self.currID += 1

    def removeFromVectorStore(self, fileName):
        documents = self.langchain_chroma.get(include=["ids", "metadatas"])
        ids_to_delete = []
        for i in range(len(documents["ids"])):
            id = documents["ids"][i]
            metadata = documents["metadatas"][i]
            if metadata["source"] == fileName:
                ids_to_delete.append(id)

        self.langchain_chroma.delete(ids_to_delete)

class QAChain:
    def __init__(self, vectorStore, llm, prompt):
        self.docsearch = vectorStore
        self.qachain = load_qa_chain(
            llm=llm, 
            chain_type="stuff",  
            prompt=prompt
        )

    def generate(self, dialog):
        input_query = dialog["dialog"][-1] if len(dialog["dialog"]) > 0 else ""
        chat_hist = ""
        if len(dialog["dialog"]) > 1:
            for line in dialog["dialog"][:-1]:
                chat_hist += f'{line["sender"]}: {line["message"]}\n'
        try:
            chat_docs = self.docsearch.similarity_search(input_query, k=1)
            output = self.qachain({"input_documents": chat_docs, "chat_history": chat_hist, "human_input": input_query})["output_text"]
        except:
            output = f'Error with model'
        return output


vectorStore = chromaDB(chroma_client, "chroma_collection", embeddings)
QAChainModel = QAChain(vectorStore, llm, CONVERSATIONQA_PROMPT)