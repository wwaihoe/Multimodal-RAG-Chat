from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.responses import PlainTextResponse
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
    retrievalModel.vectorStore.addToVectorStore(file.file, file.filename, file.size)
    print("Uploaded: ", file.filename)
    return 

@app.post("/remove")
def removeDocument(fileName: FileName):
    retrievalModel.vectorStore.removeFromVectorStore(fileName.fileName)
    print("Removed: ", fileName.fileName)
    return

@app.post("/retrieve")
def retrieveDocument(retrievalQuery: RetrievalQuery) -> RetrievalDoc:
    doc = retrievalModel.vectorStore.similarity_search(retrievalQuery.query)
    return RetrievalDoc(doc=doc)


if __name__ == '__main__':
    uvicorn.run(app, port=8002, host='0.0.0.0')