import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb


chroma_client = chromadb.PersistentClient(path="/chromadb/documents_chromadb")
collection = chroma_client.get_or_create_collection(name="chroma_collection")

def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-base")
model = AutoModel.from_pretrained("thenlper/gte-base")

def splitDocument(file):
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

def generateEmbeddings(input_texts):
    # Tokenize the input texts
    batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')

    outputs = model(**batch_dict)
    embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings

def addToVectorStore(file):
    texts = splitDocument(file)
    embeddings = generateEmbeddings(texts)
    for i in range(len(texts)):
        collection.add(
            embeddings=embeddings[i],
            documents=texts[i],
            metadatas=[{"source": file.name}],
            ids=[currentID]
        )
        currentID += 1
    
