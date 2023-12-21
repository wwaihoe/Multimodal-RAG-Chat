import os


from langchain.vectorstores import Chroma
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
#for HuggingFace
from langchain.embeddings import HuggingFaceEmbeddings


chroma_client = chromadb.PersistentClient(path="/vectorstore/documents_chromadb")
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
    
    def similarity_search(self, input):
        return self.langchain_chroma.similarity_search(input, k=1)

    def removeFromVectorStore(self, fileName):
        documents = self.langchain_chroma.get(include=["metadatas"])
        ids_to_delete = []
        for i in range(len(documents["ids"])):
            id = documents["ids"][i]
            metadata = documents["metadatas"][i]
            if metadata["source"] == fileName:
                ids_to_delete.append(id)

        self.langchain_chroma.delete(ids_to_delete)


vectorStore = chromaDB(chroma_client, "chroma_collection", embeddings)