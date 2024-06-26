from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from pydantic import BaseModel
import json
import retrievalModel



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    retrievalModel.vectorStore.chroma_client.delete_collection(name="chroma_collection")

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
    fileName: str

class FileList(BaseModel):
    files: list

class RetrievalQuery(BaseModel):
    query: str

class RetrievalDoc(BaseModel):
    doc: str
    fileNames: set[str]


@app.get("/")
def read_root():
    return {"Server": "On"}

@app.get("/load")
def loadFiles():
    fileDict = retrievalModel.vectorStore.loadFiles()
    files = []
    for fileName, fileSize in fileDict.items():
        files.append({"name": fileName, "size": fileSize})
    return FileList(files=files)

@app.post("/upload")
def uploadDocument(file: UploadFile = File(...)):
    if file.content_type == "application/pdf":
        retrievalModel.vectorStore.addToVectorStore(file.file, file.filename, file.size)
        print("PDF Uploaded: ", file.filename)
    elif file.content_type == "image/jpeg" or file.content_type == "image/png":
        retrievalModel.vectorStore.addImageToVectorStore(file.file, file.filename, file.size)
        print("Image Uploaded: ", file.filename)
    else:
        raise HTTPException(status_code=404, detail="Only PDF/JPG/PNG files are accepted!")
    return 

@app.post("/remove")
def removeDocument(fileName: FileName):
    retrievalModel.vectorStore.removeFromVectorStore(fileName.fileName)
    print("Removed: ", fileName.fileName)
    return

@app.post("/retrieve")
def retrieveDocument(retrievalQuery: RetrievalQuery) -> RetrievalDoc:
    result = retrievalModel.vectorStore.similarity_search(retrievalQuery.query)
    return RetrievalDoc(doc=result["content"], fileNames=result["file_names"])


if __name__ == '__main__':
    uvicorn.run(app, port=8002, host='0.0.0.0')