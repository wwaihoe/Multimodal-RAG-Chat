from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from pydantic import BaseModel
import retrievalModel
import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    retrievalModel.vector_store.chroma_client.delete_collection(name="chroma_collection")

app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FileName(BaseModel):
    file_name: str

class FileList(BaseModel):
    files: list

class RetrievalQuery(BaseModel):
    query: str

class RetrievalDoc(BaseModel):
    doc: str
    file_names: set[str]


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.get("/load")
def load_files():
    file_dict = retrievalModel.vector_store.load_files()
    files = []
    for file_name, file_size in file_dict.items():
        files.append({"name": file_name, "size": file_size})
    return FileList(files=files)

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if file.content_type == "application/pdf":
        retrievalModel.vector_store.add_doc_to_vectorstore(file.file, file.filename, file.size)
        print("PDF Uploaded: ", file.filename)
    elif file.content_type == "image/jpeg" or file.content_type == "image/png":
        retrievalModel.vector_store.add_image_to_vectorStore(file.file, file.filename, file.size)
        print("Image Uploaded: ", file.filename)
    elif file.content_type == "audio/mpeg":
        os.makedirs("temp", exist_ok=True)
        path = f"temp/{file.filename}"
        with open(path, "wb") as temp_file:
            temp_file.write(file.file.read())
        retrievalModel.vector_store.add_speech_to_vectorstore(path, file.filename, file.size)
        # Delete the temp_file after use
        temp_file.close()
        os.remove(path)
        print("Speech Uploaded: ", file.filename)
    else:
        raise HTTPException(status_code=404, detail="Only PDF/JPG/PNG/MP3 files are accepted!")
    return 

@app.post("/remove")
def remove_document(file_name: FileName):
    retrievalModel.vector_store.remove_from_vectorstore(file_name.file_name)
    print("Removed: ", file_name.file_name)
    return

@app.post("/retrieve")
def retrieve_document(retrieval_query: RetrievalQuery) -> RetrievalDoc:
    result = retrievalModel.vector_store.similarity_search(retrieval_query.query)
    return RetrievalDoc(doc=result["content"], file_names=result["file_names"])


if __name__ == '__main__':
    uvicorn.run(app, port=8002, host='0.0.0.0')