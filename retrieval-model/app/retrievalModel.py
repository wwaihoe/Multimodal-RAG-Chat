import os
import uuid
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from imageModels import ImageCaptionModel
from speechModels import SpeechRecognitionModel


import torch
#Use GPU if available
if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'


class ChromaDB:
    def __init__(self, embedding_function, image_caption_model, speech_recognition_model, chroma_client_dir: str="/vectorstore/documents_chromadb", collection_name: str="chroma_collection"):
        self.embedding_function = embedding_function
        self.image_caption_model = image_caption_model
        self.speech_recognition_model = speech_recognition_model
        self.chroma_client = chromadb.PersistentClient(path=chroma_client_dir)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name, embedding_function=self.embedding_function)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 250,
            length_function = len,
        )
        self.hashmap_IDs = {}
        self.hashmap_sizes = {}

    def split_document(self, file):
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
    
    def add_doc_to_vectorstore(self, file, file_name: str, file_size: float):
        texts = self.split_document(file)
        self.hashmap_IDs[file_name] = []
        self.hashmap_sizes[file_name] = file_size
        #add each text to the vector store
        for i in range(len(texts)):
            id = str(uuid.uuid4())
            self.collection.add(
                documents=[texts[i]],
                metadatas=[{"source": file_name}],
                ids=[id]
            )
            self.hashmap_IDs[file_name].append(id)
        return self.hashmap_IDs[file_name]

    def add_image_to_vectorStore(self, file, file_name: str, file_size: float):
        caption = self.image_caption_model.generate(file)
        id = str(uuid.uuid4())
        self.hashmap_IDs[file_name] = [id]
        self.hashmap_sizes[file_name] = file_size
        self.collection.add(
            documents=[caption],
            metadatas=[{"source": file_name}],
            ids=[id]
        )
        return self.hashmap_IDs[file_name]
    
    def add_speech_to_vectorstore(self, file_dir: str, file_name: str, file_size: float):
        speech = self.speech_recognition_model.generate(file_dir)
        texts = self.text_splitter.split_text(speech)
        self.hashmap_IDs[file_name] = []
        self.hashmap_sizes[file_name] = file_size
        #add each text to the vector store
        for i in range(len(texts)):
            id = str(uuid.uuid4())
            self.collection.add(
                documents=[texts[i]],
                metadatas=[{"source": file_name}],
                ids=[id]
            )
            self.hashmap_IDs[file_name].append(id)
        return self.hashmap_IDs[file_name]
    
    def load_files(self):
        return self.hashmap_sizes

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

    def remove_from_vectorstore(self, file_name):
        ids_to_delete = self.hashmapIDs.pop(file_name)
        self.hashmap_sizes.pop(file_name)
        self.collection.delete(where={"source": file_name})
        return ids_to_delete
    

class HuggingFaceEmbeddingFunction:
    def __init__(self, model_name: str="Alibaba-NLP/gte-base-en-v1.5"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)

    def __call__(self, input: list[str]):
        batch_dict = self.tokenizer(input, max_length=8192, padding=True, truncation=True, return_tensors='pt')
        outputs = self.model(**batch_dict)
        embeddings = outputs.last_hidden_state[:, 0]
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings.tolist()


#initialize the embedding function, image caption model, and vector store
#sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2", device=device)
hugging_face_ef = HuggingFaceEmbeddingFunction(model_name="Alibaba-NLP/gte-base-en-v1.5")
image_caption_model = ImageCaptionModel()
speech_recognition_model = SpeechRecognitionModel()
vector_store = ChromaDB(embedding_function = hugging_face_ef, image_caption_model = image_caption_model, speech_recognition_model = speech_recognition_model, chroma_client_dir = "/vectorstore/documents_chromadb", collection_name = "chroma_collection")