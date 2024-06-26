import os
import uuid
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from imageModels import ImageCaptionModel


import torch
#Use GPU if available
if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'


class ChromaDB:
    def __init__(self, embeddingfunction, imageCaptionModel, chroma_client_dir: str="/vectorstore/documents_chromadb", collection_name: str="chroma_collection"):
        self.embeddingfunction = embeddingfunction
        self.imageCaptionModel = imageCaptionModel
        self.chroma_client = chromadb.PersistentClient(path=chroma_client_dir)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name, embedding_function=self.embeddingfunction)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap  = 150,
            length_function = len,
        )
        self.hashmapIDs = {}
        self.hashmapSizes = {}

    def splitDocument(self, file):
        reader = PdfReader(file)
        page_delimiter = '\n'
        doc = ""
        #exclude cover page and table of contexts
        for page in reader.pages:
            page_text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)
            page_text += page_delimiter
            doc += page_text
        #split document using recursive splitter
        texts = self.text_splitter.split_text(doc)
        return texts
    
    def addToVectorStore(self, file, fileName: str, fileSize: float):
        texts = self.splitDocument(file)
        self.hashmapIDs[fileName] = []
        self.hashmapSizes[fileName] = fileSize
        #add each text to the vector store
        for i in range(len(texts)):
            id = str(uuid.uuid4())
            self.collection.add(
                documents=[texts[i]],
                metadatas=[{"source": fileName}],
                ids=[id]
            )
            self.hashmapIDs[fileName].append(id)
        return self.hashmapIDs[fileName]

    def addImageToVectorStore(self, file, fileName: str, fileSize: float):
        caption = self.imageCaptionModel.generate(file)
        id = str(uuid.uuid4())
        self.hashmapIDs[fileName] = [id]
        self.hashmapSizes[fileName] = fileSize
        self.collection.add(
            documents=[caption],
            metadatas=[{"source": fileName}],
            ids=[id]
        )
        return self.hashmapIDs[fileName]
    
    def loadFiles(self):
        return self.hashmapSizes

    def similarity_search(self, input: str, k: int = 2):
        content = ""
        result = self.collection.query(
            query_texts=[input],
            n_results=k
        )
        for doc in result["documents"][0]:
            content += doc
            content += "\n\n-----\n\n"
        file_names = set()
        for metadata in result["metadatas"][0]:
            file_names.add(metadata["source"])
        return {"content": content, "file_names": file_names}

    def removeFromVectorStore(self, fileName):
        ids_to_delete = self.hashmapIDs.pop(fileName)
        self.hashmapSizes.pop(fileName)
        self.collection.delete(where={"source": fileName})
        return ids_to_delete


#initialize the embedding function, image caption model, and vector store
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2", device=device)
imageCaptionModel = ImageCaptionModel()
vectorStore = ChromaDB(embeddingfunction = sentence_transformer_ef, imageCaptionModel = imageCaptionModel, chroma_client_dir = "/vectorstore/documents_chromadb", collection_name = "chroma_collection")